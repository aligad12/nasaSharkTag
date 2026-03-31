namespace NasaTest.Services
{
    using Microsoft.Extensions.Hosting;
    using Microsoft.Extensions.DependencyInjection;
    using Shark.InfraStructure.AppDbContext;
    using System.Threading;
    using System.Threading.Tasks;

    public class MqttBackgroundService : BackgroundService
    {
        private readonly IServiceScopeFactory _scopeFactory;

        public MqttBackgroundService(IServiceScopeFactory scopeFactory)
        {
            _scopeFactory = scopeFactory;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            using var scope = _scopeFactory.CreateScope();

            var dbContext = scope.ServiceProvider.GetRequiredService<SharkApp>();
            var aiDataService = scope.ServiceProvider.GetRequiredService<AiDataService>();
            var locationService = scope.ServiceProvider.GetRequiredService<LocationService>();

            await locationService.ConnectAsync(); // Singleton
            await aiDataService.ConnectAsync();   // Scoped, runs once
            // ممكن تضيف أي تعامل مع dbContext هنا لو محتاج
        }
    }
}