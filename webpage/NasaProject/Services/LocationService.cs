using MQTTnet.Formatter;
using MQTTnet;
using System.Net;
using System.Text;
using NasaTest.Models;
using NasaTest.Controllers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using NasaTest.Services;

public class LocationService
{
	private readonly IMqttClient _client;
	private readonly IHubContext<LocationHub> _hubContext;
    private readonly IConfiguration _configuration;

    public OtherProperties? LastProperties { get; private set; }   // هنخزن آخر رسالة هنا

	public LocationService(IHubContext<LocationHub> hubContext , IConfiguration configuration)
	{
		var factory = new MqttClientFactory();
		_client = factory.CreateMqttClient();
		_hubContext = hubContext;
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
				Console.WriteLine("✅ Connected to Adafruit MQTT broker.");
				await _client.SubscribeAsync("abdelrhmanatta/feeds/shark");
			}

			// نخلي الهاندلر يتنفذ مع أي رسالة جديدة
			_client.ApplicationMessageReceivedAsync += async e =>
			{
				var payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
				string[] parts = payload.Split(',');
                LastProperties = new OtherProperties
                {
                    Longitude = Convert.ToDouble(parts[0]),
                    Latitude = Convert.ToDouble(parts[1]),
                    Temperatue = Convert.ToDouble(parts[2]),
                    Pressure = Convert.ToDouble(parts[3]),
                    EatingProbability = Convert.ToDouble(parts[4])
                };
                await _hubContext.Clients.All.SendAsync("ReceiveLocation", LastProperties);
				Console.WriteLine($"✅ Updated: {LastProperties.Longitude}, {LastProperties.Latitude}");
			};
		}
	}






