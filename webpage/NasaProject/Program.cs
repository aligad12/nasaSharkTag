using Microsoft.EntityFrameworkCore;
using NasaTest.Services;
using Shark.InfraStructure.AppDbContext;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<LocationService>();
builder.Services.AddSignalR();
builder.Services.AddSingleton<MqttBackgroundService>();
builder.Services.AddHostedService<MqttBackgroundService>();
builder.Services.AddDbContext<SharkApp>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<SharkService>();
builder.Services.AddScoped<AiDataService>();



var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.MapHub<LocationHub>("/locationhub");
app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
