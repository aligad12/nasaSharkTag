namespace NasaTest.Services
{
	using Microsoft.AspNetCore.SignalR;
	using NasaTest.Models;
    using Shark.InfraStructure.Models;

    public class LocationHub : Hub
	{
		public async Task SendLocation(OtherProperties properties, SharkEntity shark)
		{
			await Clients.All.SendAsync("ReceiveLocation", properties);

            await Clients.All.SendAsync("ReceiveShark", shark);


        }
    }
}
