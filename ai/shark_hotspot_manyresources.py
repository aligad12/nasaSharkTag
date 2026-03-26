# shark_hotspot_from_modis_only.py
# Uses only the provided MODIS monthly files (no SWOT, no JSON).
# Save next to the folder "monthly-data-folder" or change base_dir.

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
import warnings
import cartopy.crs as ccrs
import cartopy.feature as cfeature

warnings.simplefilter("default")

# ---------- Utility functions ----------
def detect_coord_name(ds):
    coords = list(ds.coords)
    latname = None
    lonname = None
    for name in coords:
        n = name.lower()
        if 'lat' in n and latname is None:
            latname = name
        if 'lon' in n and lonname is None:
            lonname = name
    # fallback: pick first two coords
    if latname is None:
        latname = coords[0]
    if lonname is None:
        lonname = coords[1] if len(coords) > 1 else coords[0]
    return latname, lonname

def find_data_var(ds, keywords):
    # find a data variable with any of the keywords in its name (case-insensitive)
    for v in ds.data_vars:
        vn = v.lower()
        for kw in keywords:
            if kw in vn:
                return v
    # fallback: return first variable
    return list(ds.data_vars)[0]

def take_first_time_if_present(da):
    if 'time' in da.dims:
        return da.isel(time=0)
    else:
        return da

def safe_open(ds_path):
    # use xarray to open dataset (with decoding off for some attributes if needed)
    return xr.open_dataset(ds_path, decode_times=True, mask_and_scale=True)

# ---------- Files (only these) ----------
# ---------- Files (MODIS + PACE + SM) ----------
monthly_dir = "monthly-data-folder"

files = {
    # MODIS files
    "chl":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.CHL.chlor_a.4km.nc"),
    "flh":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.FLH.ipar.4km.nc"),
    "aph":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.IOP.aph_443.4km.nc"),
    "kd":   os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.KD.Kd_490.4km.nc"),
    "nsst": os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.NSST.sst.4km.nc"),
    "poc":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.POC.poc.4km.nc"),
    "aot":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.RRS.aot_869.4km.nc"),
    "sst":  os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.SST.sst.4km.nc"),
    "sst4": os.path.join(monthly_dir, "AQUA_MODIS.20240601_20240630.L3m.MO.SST4.sst4.4km.nc"),

    # ✅ Added PACE datasets
    "pace_rrs_202507": os.path.join(monthly_dir, "PACE_OCI.20250701.L3m.DAY.RRS.V3_1.Rrs.0p1deg.NRT.nc"),
    "pace_aer_202508": os.path.join(monthly_dir, "PACE_OCI.20250801.L3m.DAY.AER_UAA.V3_1.0p1deg.NRT.nc"),
    "pace_aer_202509": os.path.join(monthly_dir, "PACE_OCI.20250915.L3m.DAY.AER_UAA.V3_1.1deg.NRT.nc"),
    "pace_aer_202510": os.path.join(monthly_dir, "PACE_OCI.20251004.L3m.DAY.AER_UAA.V3_1.1deg.NRT.nc"),

    # ✅ Added SM datasets (salinity maps)
    "sm_1": os.path.join(monthly_dir, "SM_D2010152_Map_SATSSS_data_1day_1deg.nc"),
    "sm_2": os.path.join(monthly_dir, "SM_D2010154_Map_SATSSS_data_3days.nc"),
    "sm_3": os.path.join(monthly_dir, "SM_D2010155_Map_SATSSS_data_1day.nc"),

    # ✅ Added NeurOST SSH-SST datasets (eddy dynamics)
    "neur_ssh_sst_1": os.path.join(monthly_dir, "NeurOST_SSH-SST_20241208_20250206.nc"),
    "neur_ssh_sst_2": os.path.join(monthly_dir, "NeurOST_SSH-SST_20241209_20250206.nc"),
    "neur_ssh_sst_3": os.path.join(monthly_dir, "NeurOST_SSH-SST_20241210_20250206.nc"),
    "neur_ssh_sst_4": os.path.join(monthly_dir, "NeurOST_SSH-SST_20241211_20250206.nc"),
}

# Verify files exist
for k, p in files.items():
    if not os.path.exists(p):
        raise FileNotFoundError(f"Required file for {k} not found at: {p}")


# ---------- Open datasets and extract main DataArrays ----------
ds_objs = {}
for key, path in files.items():
    ds = safe_open(path)
    ds_objs[key] = ds

# Use chlorophyll dataset as reference grid
chl_ds = ds_objs["chl"]
chl_lat_name, chl_lon_name = detect_coord_name(chl_ds)
chl_var = find_data_var(chl_ds, ['chlor', 'chl', 'chlorophyll', 'chlor_a', 'chl_a'])
print("Reference (CHL):", chl_lat_name, chl_lon_name, chl_var)

chl_da = take_first_time_if_present(chl_ds[chl_var]).squeeze()

# Build a target grid (1D coords) from the chlorophyll dataset
if chl_lat_name in chl_da.coords:
    lat_vals = chl_da[chl_lat_name].values
else:
    lat_vals = chl_ds.coords[chl_lat_name].values
if chl_lon_name in chl_da.coords:
    lon_vals = chl_da[chl_lon_name].values
else:
    lon_vals = chl_ds.coords[chl_lon_name].values

# ensure lon range consistent: convert longitudes to -180..180 if needed for interpolation
def normalize_lon_array(lon):
    lon = np.array(lon)
    if lon.max() > 180:
        lon = ((lon + 180) % 360) - 180
    return lon

lon_vals = normalize_lon_array(lon_vals)

# Create a target DataArray grid (xarray-friendly)
target_lat = xr.DataArray(lat_vals, dims=[chl_lat_name], coords={chl_lat_name: lat_vals})
target_lon = xr.DataArray(lon_vals, dims=[chl_lon_name], coords={chl_lon_name: lon_vals})

# Function to extract and regrid each variable onto the chlorophyll grid
def extract_and_regrid(ds_obj, prefer_keys=None, target_lat_name=chl_lat_name, target_lon_name=chl_lon_name):
    ds = ds_obj
    latname, lonname = detect_coord_name(ds)
    varname = find_data_var(ds, prefer_keys if prefer_keys else [])
    da = take_first_time_if_present(ds[varname]).squeeze()

    # Normalize lon coords of source to -180..180 to match target
    if lonname in da.coords:
        src_lon = da[lonname].values
        src_lon = normalize_lon_array(src_lon)  # ✅ Always normalize
        da = da.assign_coords({lonname: src_lon})


    # If dims are (y,x) or (lat,lon) with names matching target -> select or align
    try:
        # prefer xr.align/interp: if coords are 1D and monotonic it's fine
        # create a new small dataset with the da and then interp to target coords
        coords = {latname: target_lat, lonname: target_lon}
        # Use .interp for float coords (will create NaNs where missing)
        da_on_target = da.interp(coords, method="nearest")
    except Exception:
        # fallback: try indexing by nearest values manually using xarray's sel with method='nearest'
        try:
            da_on_target = da.sel({latname: target_lat, lonname: target_lon}, method="nearest")
        except Exception:
            # last fallback: attempt to reshape / broadcast if already matching shape
            da_on_target = da

            # ---- NEW: apply ocean mask from chlorophyll ----
    if "chlor_a" in features:
        chl_mask = np.isfinite(features["chlor_a"].values)
        try:
            arr = da_on_target.values
            arr[~chl_mask] = np.nan
            da_on_target = xr.DataArray(
                arr, dims=da_on_target.dims, coords=da_on_target.coords, attrs=da_on_target.attrs
            )
        except Exception:
            pass

    # Ensure the returned DataArray uses the target coordinate names
    if detect_coord_name(da_on_target) != (target_lat_name, target_lon_name):
        # rename dims if necessary
        try:
            da_on_target = da_on_target.rename({latname: target_lat_name, lonname: target_lon_name})
        except Exception:
            pass
    return da_on_target

# Extract/regrid feature DataArrays
features = {}
features['chlor_a'] = chl_da  # already on the target grid

# feature extraction list and preferred keywords
pref_map = {
    # MODIS
    "flh": ['flh', 'ipar', 'photic'],
    "aph": ['aph', 'aph_443', 'aph443', 'iop'],
    "kd": ['kd', 'kd_490', 'kd490'],
    "nsst": ['nsst', 'nsst.sst', 'nsst_sst', 'nsst'],
    "poc": ['poc', 'poc.'],
    "aot": ['aot', 'aot_869', 'aerosol'],
    "sst": ['sst', 'sea_surface_temp', 'sea_surface_temperature'],
    "sst4": ['sst4', 'sst4.'],

    # PACE
    "pace_rrs_202507": ['rrs', 'r_rs', 'reflectance'],
    "pace_aer_202508": ['aer', 'aerosol', 'aot', 'uaa'],
    "pace_aer_202509": ['aer', 'aerosol', 'aot', 'uaa'],
    "pace_aer_202510": ['aer', 'aerosol', 'aot', 'uaa'],

    # SM (salinity maps)
    "sm_1": ['sss', 'salinity', 'sss_mean'],
    "sm_2": ['sss', 'salinity'],
    "sm_3": ['sss', 'salinity'],

    # NeurOST SSH-SST
    "neur_ssh_sst_1": ['ssh', 'sea_surface_height', 'sst', 'eddy'],
    "neur_ssh_sst_2": ['ssh', 'sea_surface_height', 'sst', 'eddy'],
    "neur_ssh_sst_3": ['ssh', 'sea_surface_height', 'sst', 'eddy'],
    "neur_ssh_sst_4": ['ssh', 'sea_surface_height', 'sst', 'eddy'],

}

for key in ['flh', 'aph', 'kd', 'nsst', 'poc', 'aot', 'sst', 'sst4']:
    ds_obj = ds_objs[key]
    da_reg = extract_and_regrid(ds_obj, prefer_keys=pref_map.get(key, None))
    features[key] = take_first_time_if_present(da_reg).squeeze()


# ---------- Extract NeurOST SSH-SST eddy features ----------
neur_keys = ['neur_ssh_sst_1', 'neur_ssh_sst_2', 'neur_ssh_sst_3', 'neur_ssh_sst_4']
for key in neur_keys:
    ds_obj = ds_objs[key]
    da_reg = extract_and_regrid(ds_obj, prefer_keys=pref_map.get(key, None))
    features[key] = take_first_time_if_present(da_reg).squeeze()


def da_to_grid(da):
    # Ensure dims are (lat, lon)
    latdim, londim = detect_coord_name(da)
    arr = da.values
    # If 1D x 1D coords, arr shape should be (len(lat), len(lon)) or similar
    return arr

grid_arrays = {}
for k, da in features.items():
    arr = da_to_grid(da)
    grid_arrays[k] = arr

# Use mask of valid chlorophyll pixels as valid grid mask
chl_grid = grid_arrays['chlor_a']
grid_shape = chl_grid.shape
print("Grid shape:", grid_shape)

# Flatten arrays and build feature matrix
flat_features = {}
for k, arr in grid_arrays.items():
    flat_features[k] = arr.flatten()

n_pixels = flat_features['chlor_a'].size

# Build feature matrix: stack available features in a deterministic order
feature_keys = [
    'chlor_a', 'sst', 'sst4', 'nsst', 'poc', 'kd', 'aph', 'flh', 'aot',
    # Added dynamic ocean structure (NeurOST)
    'neur_ssh_sst_1', 'neur_ssh_sst_2', 'neur_ssh_sst_3', 'neur_ssh_sst_4'
]
X_cols = []
col_names = []
for k in feature_keys:
    if k in flat_features:
        X_cols.append(flat_features[k])
        col_names.append(k)

X = np.vstack(X_cols).T  # shape (n_pixels, n_features)

# Create mask of pixels where at least chlor and sst exist (or at least one non-NaN)
mask_valid = np.isfinite(flat_features['chlor_a']) & np.isfinite(flat_features.get('sst', flat_features['chlor_a']))
print("Valid pixels count:", np.sum(mask_valid))

# Fill remaining missing feature values for training with per-feature mean (computed on valid mask)
X_filled = X.copy()
for j in range(X_filled.shape[1]):
    col = X_filled[:, j]
    col_valid = np.isfinite(col) & mask_valid
    if np.any(col_valid):
        mean_val = np.nanmean(col[col_valid])
    else:
        mean_val = 0.0
    # fill only where nan
    col[np.isnan(col)] = mean_val
    X_filled[:, j] = col

# Standardize features (fit only on valid pixels)
scaler = StandardScaler()
X_valid_scaled = scaler.fit_transform(X_filled[mask_valid, :])
print("Feature matrix shape (valid):", X_valid_scaled.shape)


def find_index(name):
    try:
        return col_names.index(name)
    except ValueError:
        return None

idx_chl = find_index('chlor_a')
idx_sst = find_index('sst') if find_index('sst') is not None else find_index('nsst') or find_index('sst4')

if idx_chl is None or idx_sst is None:
    # fallback: if missing sst, use chlor only threshold to make a binary map
    print("Warning: SST or CHL index missing from features; using CHL-only heuristic for labels.")
    y_valid = (X_valid_scaled[:, idx_chl] > 0.75).astype(int)  # top-chl regions
else:
    # Use thresholds on scaled features
    chl_scaled = X_valid_scaled[:, idx_chl]
    sst_scaled = X_valid_scaled[:, idx_sst]
    y_valid = ((chl_scaled > 0.5) & (sst_scaled < -0.2)).astype(int)

# Check class balance
unique, counts = np.unique(y_valid, return_counts=True)
print("Label distribution (valid pixels):", dict(zip(unique, counts)))

if len(unique) == 1:
    print("Only one class in labels - RF will be trained on single class (predict_proba fallback to predict).")

# Subsample for training if too many pixels
n_max_samples = 20000
n_samples = min(n_max_samples, X_valid_scaled.shape[0])
rng = np.random.RandomState(42)
idx_sample = rng.choice(np.arange(X_valid_scaled.shape[0]), size=n_samples, replace=False)

X_sample = X_valid_scaled[idx_sample, :]
y_sample = y_valid[idx_sample]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.2, random_state=42, stratify=y_sample if len(np.unique(y_sample))>1 else None)

clf = RandomForestClassifier(n_estimators=50, max_depth=12, n_jobs=-1, random_state=42, min_samples_leaf=10)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, zero_division=0))

# Predict probabilities for all valid pixels
if len(clf.classes_) == 1:
    # fallback: classifier only learned one class -> use predict (0/1)
    probs_valid = clf.predict(X_valid_scaled).astype(float)
else:
    probs_valid = clf.predict_proba(X_valid_scaled)[:, 1]

# construct full probability map and reshape to grid
prob_full = np.full(n_pixels, np.nan)
prob_full[mask_valid] = probs_valid
prob_map = prob_full.reshape(grid_shape)


try:
    # If coordinates are 1D, create meshgrid; if 2D coordinates exist, use them
    if chl_lat_name in chl_ds.coords and chl_lon_name in chl_ds.coords:
        lat_1d = chl_ds[chl_lat_name].values
        lon_1d = chl_ds[chl_lon_name].values
        lon2d, lat2d = np.meshgrid(lon_1d, lat_1d)
    else:
        # attempt to read coords from the DataArray
        lat_1d = chl_da[chl_lat_name].values
        lon_1d = chl_da[chl_lon_name].values
        lon2d, lat2d = np.meshgrid(lon_1d, lat_1d)
    # normalize lon for plotting to -180..180
    lon2d = ((lon2d + 180) % 360) - 180
except Exception:
    # fallback: simple index grid
    lat2d = np.arange(grid_shape[0])[:, None] * np.ones((1, grid_shape[1]))
    lon2d = np.arange(grid_shape[1])[None, :] * np.ones((grid_shape[0], 1))

# Flip map if needed when lat decreases
if lat2d.shape == prob_map.shape:
    if lat2d[0,0] > lat2d[-1,0]:
        prob_map = np.flipud(prob_map)
        lat2d = np.flipud(lat2d)


# Create a map projection
proj = ccrs.PlateCarree()

plt.figure(figsize=(12, 6))
ax = plt.axes(projection=proj)

# Add map features
ax.coastlines(resolution="110m", linewidth=0.8)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.7)
ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
ax.add_feature(cfeature.BORDERS, linestyle='--', linewidth=0.5)
ax.gridlines(draw_labels=True, color='gray', alpha=0.3, linestyle='--')

# Plot probability map
pcm = ax.pcolormesh(
    lon2d, lat2d, prob_map,
    transform=ccrs.PlateCarree(),
    shading='auto', cmap='coolwarm', vmin=0, vmax=1
)

# Overlay eddy contours if available
try:
    eddy_da = features['neur_ssh_sst_1']

    # Normalize eddy longitude coords to match MODIS
    latname, lonname = detect_coord_name(eddy_da)
    if lonname in eddy_da.coords:
        eddy_da = eddy_da.assign_coords({lonname: normalize_lon_array(eddy_da[lonname].values)})

    # Apply ocean mask again just to be safe
    if "chlor_a" in features:
        chl_mask = np.isfinite(features["chlor_a"].values)
        eddy_vals = eddy_da.values
        eddy_vals[~chl_mask] = np.nan
        eddy_da = xr.DataArray(eddy_vals, dims=eddy_da.dims, coords=eddy_da.coords)

    # Now contour it safely
    ax.contour(
        lon2d, lat2d, eddy_da,
        transform=ccrs.PlateCarree(),
        colors='k', linewidths=0.4, alpha=0.5
    )

except Exception:
    pass

# Add colorbar and title
cbar = plt.colorbar(pcm, orientation='horizontal', pad=0.05, shrink=0.8)
cbar.set_label("Predicted Shark Hotspot Probability")

ax.set_title("Predicted Shark Hotspots (with Eddy Contours)")
plt.tight_layout()
plt.show()



# Optionally save the probability map to a NetCDF file for later use
out_nc = os.path.join("monthly-data-folder", "modis_only_shark_hotspot_prob_map.nc")
try:
    ds_out = xr.Dataset(
        {
            "hotspot_prob": ( (chl_lat_name, chl_lon_name), prob_map )
        },
        coords={
            chl_lat_name: (chl_lat_name, lat_vals),
            chl_lon_name: (chl_lon_name, lon_vals)
        }
    )
    ds_out.to_netcdf(out_nc)
    print("Saved probability map to:", out_nc)
except Exception as e:
    print("Could not save NetCDF:", e)
