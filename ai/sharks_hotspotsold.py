import json
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
import warnings

warnings.simplefilter("default")

def detect_coord_name(ds, prefer_lat='lat', prefer_lon='lon'):
    coords = list(ds.coords)
    latname = None
    lonname = None
    for name in coords:
        n = name.lower()
        if 'lat' in n and latname is None:
            latname = name
        if 'lon' in n and lonname is None:
            lonname = name
    if latname is None:
        latname = coords[0]
    if lonname is None:
        lonname = coords[1] if len(coords) > 1 else coords[0]
    return latname, lonname

def find_data_var(ds, keywords):
    for v in ds.data_vars:
        vn = v.lower()
        for kw in keywords:
            if kw in vn:
                return v
    return list(ds.data_vars)[0]

def take_first_time_if_present(var):
    if 'time' in var.dims:
        return var.isel(time=0)
    else:
        return var

def latlon_to_cartesian(lat_deg, lon_deg):
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    x = np.cos(lat) * np.cos(lon)
    y = np.cos(lat) * np.sin(lon)
    z = np.sin(lat)
    return np.column_stack([x, y, z])

def safe_float_from_str(s):
    if isinstance(s, (int, float, np.floating, np.integer)):
        return float(s)
    if isinstance(s, str):
        s2 = ''.join(ch for ch in s if (ch.isdigit() or ch=='.' or ch=='-' or ch=='+'))
        try:
            return float(s2)
        except:
            return np.nan
    return np.nan

modis_chl_file = r"monthly-data-folder\AQUA_MODIS.20240601_20240630.L3m.MO.CHL.chlor_a.4km.nc"
modis_sst_file = r"monthly-data-folder\AQUA_MODIS.20240601_20240630.L3m.MO.SST.sst.4km.nc"

modis_chl_ds = xr.open_dataset(modis_chl_file)
modis_sst_ds = xr.open_dataset(modis_sst_file)

modis_lat_name, modis_lon_name = detect_coord_name(modis_chl_ds)
chl_var = find_data_var(modis_chl_ds, ['chlor', 'chl'])
sst_var = find_data_var(modis_sst_ds, ['sst', 'sea_surface_temperature', 'sea_surface_temp'])
print("MODIS coords & vars:", modis_lat_name, modis_lon_name, chl_var, sst_var)

chl_da = take_first_time_if_present(modis_chl_ds[chl_var]).squeeze()
sst_da = take_first_time_if_present(modis_sst_ds[sst_var]).squeeze()

swot_file = r"monthly-data-folder\SWOT_L2_LR_SSH_Basic_016_541_20240617T115123_20240617T124251_PIC0_01_subsetted_20240619T235226Z_C2799465428-POCLOUD_merged.nc4"
swot_ds = xr.open_dataset(swot_file)

swot_lat_name, swot_lon_name = detect_coord_name(swot_ds)
swot_var = find_data_var(swot_ds, ['ssh', 'ssh_karin', 'sea_surface_height', 'height'])
print("SWOT coords & var:", swot_lat_name, swot_lon_name, swot_var)

swot_lat = swot_ds[swot_lat_name].values.flatten()
swot_lon = swot_ds[swot_lon_name].values.flatten()
swot_val = swot_ds[swot_var].values.flatten()
valid_swot_mask = np.isfinite(swot_lat) & np.isfinite(swot_lon) & np.isfinite(swot_val)
swot_lat = swot_lat[valid_swot_mask]
swot_lon = swot_lon[valid_swot_mask]
swot_val = swot_val[valid_swot_mask]
print("SWOT valid count:", swot_lat.size)

lat_min, lat_max = float(np.nanmin(swot_lat)), float(np.nanmax(swot_lat))
lon_min, lon_max = float(np.nanmin(swot_lon)), float(np.nanmax(swot_lon))

modis_lon_vals = modis_chl_ds[modis_lon_name].values if modis_lon_name in modis_chl_ds.coords else modis_chl_ds.coords[modis_lon_name].values
if modis_lon_vals.min() >= 0 and np.nanmin(swot_lon) < 0:
    swot_lon = np.where(swot_lon < 0, swot_lon + 360, swot_lon)
    lon_min, lon_max = float(np.nanmin(swot_lon)), float(np.nanmax(swot_lon))
    print("Converted SWOT lon to 0..360 to match MODIS.")

modis_lat_vals = chl_da[modis_lat_name].values if modis_lat_name in chl_da.coords else chl_da.coords[modis_lat_name].values
modis_lon_vals = chl_da[modis_lon_name].values if modis_lon_name in chl_da.coords else chl_da.coords[modis_lon_name].values

if modis_lat_vals[0] > modis_lat_vals[-1]:
    lat_slice = slice(lat_max, lat_min)
else:
    lat_slice = slice(lat_min, lat_max)
lon_slice = slice(lon_min, lon_max)

modis_chl_subset = chl_da.sel({modis_lat_name: lat_slice, modis_lon_name: lon_slice})
modis_sst_subset = sst_da.sel({modis_lat_name: lat_slice, modis_lon_name: lon_slice})

print("MODIS subset shapes:", modis_chl_subset.shape, modis_sst_subset.shape)

modis_lat = modis_chl_subset[modis_lat_name].values
modis_lon = modis_chl_subset[modis_lon_name].values
lon2d, lat2d = np.meshgrid(modis_lon, modis_lat)
grid_shape = lat2d.shape
print("Grid shape:", grid_shape)

stride = 10
swot_lat_sub = swot_lat[::stride]
swot_lon_sub = swot_lon[::stride]
swot_val_sub = swot_val[::stride]
swot_xyz = latlon_to_cartesian(swot_lat_sub, swot_lon_sub)
grid_xyz = latlon_to_cartesian(lat2d.ravel(), lon2d.ravel())

tree = cKDTree(swot_xyz)
dist, idx = tree.query(grid_xyz, k=1)

earth_r = 6371000.0
max_dist_m = 50_000.0
ang = max_dist_m / earth_r
chord_thresh = 2.0 * np.sin(ang/2.0)
mapped_vals = swot_val_sub[idx]
mapped_vals[dist > chord_thresh] = np.nan

pace_sst_on_modis = np.full(grid_shape, np.nan)
pace_sst_on_modis.ravel()[:] = mapped_vals
print("Mapped SWOT -> MODIS; assigned cells:", np.sum(np.isfinite(pace_sst_on_modis)))

json_path = r"json\shark_datasets_with_AI_predictions1.json"
with open(json_path, "r") as f:
    shark_data = json.load(f)

shark_points = []
for record in shark_data:
    loc = record.get("location", None)
    if loc is None:
        continue
    if isinstance(loc, (list, tuple)) and len(loc) >= 2:
        lat, lon = float(loc[0]), float(loc[1])
    elif isinstance(loc, dict):
        lat = float(loc.get("lat") or loc.get("latitude"))
        lon = float(loc.get("lon") or loc.get("longitude"))
    else:
        continue
    depth = safe_float_from_str(record.get("depth", np.nan))
    temp = safe_float_from_str(record.get("surface_temperature", np.nan))
    prob = record.get("feeding_probability", np.nan)
    try:
        prob = float(prob)
    except:
        prob = np.nan
    shark_points.append([lat, lon, depth, temp, prob])
shark_points = np.array(shark_points)
print("Loaded shark records:", shark_points.shape)

chl_flat = modis_chl_subset.values.flatten()
sst_flat = modis_sst_subset.values.flatten()
pace_flat = pace_sst_on_modis.flatten()

assert chl_flat.size == sst_flat.size == pace_flat.size, "Flattened arrays must match length"

mask_modis = np.isfinite(chl_flat) & np.isfinite(sst_flat)
print("Valid MODIS pixels:", np.sum(mask_modis))

pace_flat_filled = pace_flat.copy()
if np.isnan(pace_flat_filled).all():
    pace_flat_filled = np.zeros_like(pace_flat_filled)
else:
    mean_pace = np.nanmean(pace_flat_filled)
    pace_flat_filled[np.isnan(pace_flat_filled)] = mean_pace

X = np.column_stack([chl_flat[mask_modis], sst_flat[mask_modis], pace_flat_filled[mask_modis]])
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("X_scaled shape:", X_scaled.shape)

y = ((X_scaled[:, 0] > 0.5) & (X_scaled[:, 1] < -0.2)).astype(int)
if len(np.unique(y)) == 1:
    print("Warning: Only one class present in labels. RF will be trained on single class (predict_proba may fail).")

n_samples = min(20000, len(X_scaled))
X_small, y_small = resample(X_scaled, y, n_samples=n_samples, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X_small, y_small, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=30, max_depth=10, n_jobs=-1, random_state=42, min_samples_leaf=20)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, zero_division=0))

pred_map = np.full(grid_shape, np.nan)
if len(clf.classes_) == 1:
    probs = clf.predict(X_scaled)  
    probs = probs.astype(float)
else:
    probs = clf.predict_proba(X_scaled)[:, 1]

flat_pred_map = pred_map.ravel()
flat_pred_map[mask_modis] = probs
pred_map = flat_pred_map.reshape(grid_shape)

if modis_lat[0] > modis_lat[-1]:
    pred_map = np.flipud(pred_map)
    modis_lat = modis_lat[::-1]
    lat2d = np.flipud(lat2d)
    lon2d = np.flipud(lon2d)

plt.figure(figsize=(10, 6))
pcm = plt.pcolormesh(lon2d, lat2d, pred_map, shading='auto', cmap='coolwarm', vmin=0, vmax=1)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Predicted Shark Hotspots Probability (0-1)")
plt.colorbar(pcm, label="Hotspot Probability")
plt.tight_layout()
plt.show()