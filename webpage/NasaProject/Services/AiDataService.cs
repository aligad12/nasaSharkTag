using Microsoft.AspNetCore.SignalR;
using MQTTnet.Formatter;
using MQTTnet;
using NasaTest.Models;
using System.Net;
using System.Text;
using Shark.InfraStructure.Models;
using Microsoft.Extensions.Configuration;

namespace NasaTest.Services
{
    public class AiDataService
    {

        private readonly IMqttClient _client;
        private readonly IHubContext<LocationHub> _hubContext;
        
        private readonly IServiceScopeFactory _scopeFactory;
        private readonly IConfiguration _configuration;


        public OtherProperties? LastProperties { get; private set; }   // هنخزن آخر رسالة هنا
        public SharkEntity? sharkEntity { get; private set; }

        public AiDataService(IHubContext<LocationHub> hubContext, SharkService sharkService,IServiceScopeFactory scopeFactory, IConfiguration configuration)
        {
            var factory = new MqttClientFactory();
            _client = factory.CreateMqttClient();
            _hubContext = hubContext;
           
            _scopeFactory = scopeFactory;
            _configuration = configuration;

        }

        public async Task ConnectAsync()
        {
            var options = new MqttClientOptions
            {
                ClientId = "mvc-subscriber",
                ProtocolVersion = MqttProtocolVersion.V311,
                Credentials = new MqttClientCredentials("Abozeid125", Encoding.UTF8.GetBytes("aio_RpPZ87yozskhaMQpNvtrYrZ8ay5x")),


                ChannelOptions = new MqttClientTcpOptions
                {
                    RemoteEndpoint = new DnsEndPoint("io.adafruit.com", 1883),
                }
            };

            if (!_client.IsConnected)
            {
                await _client.ConnectAsync(options);
            }
            if (_client.IsConnected)
            {
                Console.WriteLine("✅ Connected to Adafruit MQTT broker 2.");
                await _client.SubscribeAsync("mariamramy/feeds/ai-data");
            }

            // نخلي الهاندلر يتنفذ مع أي رسالة جديدة
            _client.ApplicationMessageReceivedAsync += async e =>
            {
                try
                {
                    var payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
                    Console.WriteLine($"📩 Payload: {payload}");
                    string[] parts = payload.Split(',');

                    using var scope = _scopeFactory.CreateScope();
                    var _sharkService = scope.ServiceProvider.GetRequiredService<SharkService>();

                    DateTime time = new DateTime(
                        Convert.ToInt16(parts[0]),
                        Convert.ToInt16(parts[1]),
                        Convert.ToInt16(parts[2]),
                        Convert.ToInt16(parts[3]),
                        Convert.ToInt16(parts[4]),
                        Convert.ToInt16(parts[5])
                    );

                    int id = Convert.ToInt16(parts[6]);

                    SharkEntity? shark2 = await _sharkService.GetSharkByIdAsync(id);
                    int added = -1;

                    if (shark2 == null)
                    {
                        SharkEntity shark3 = new SharkEntity
                        {
                           
                            Depth = Convert.ToDouble(parts[7]),
                            Temperatue = Convert.ToDouble(parts[8]),
                            Longitude = Convert.ToDouble(parts[9]),
                            Latitude = Convert.ToDouble(parts[10]),
                            EatingProbability = Convert.ToDouble(parts[11]),
                            Time = time
                        };

                        added = await _sharkService.AddShark(shark3);
                        shark2 = shark3;
                    }
                    else
                    {
                        shark2.Depth = Convert.ToDouble(parts[7]);
                        shark2.Temperatue = Convert.ToDouble(parts[8]);
                        shark2.Longitude = Convert.ToDouble(parts[9]);
                        shark2.Latitude = Convert.ToDouble(parts[10]);
                        shark2.EatingProbability = Convert.ToDouble(parts[11]);
                        shark2.Time = time;

                        await _sharkService.UpdateSharkAsync(shark2);
                        added = 0;
                    }

                    sharkEntity = shark2;

                    await _hubContext.Clients.All.SendAsync("ReceiveShark", sharkEntity);
                    Console.WriteLine($"✅ Updated: {sharkEntity.Longitude}, {sharkEntity.Latitude}, {time}, id = {id}, depth = {sharkEntity.Depth}, added = {added}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"❌ Error in handler: {ex.Message}");
                }
            };
            ;
        }


    }
}
