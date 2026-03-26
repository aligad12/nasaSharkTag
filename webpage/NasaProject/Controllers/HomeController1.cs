using Microsoft.AspNetCore.Mvc;
using NasaTest.Models;
using NasaTest.Services;
using Shark.InfraStructure.Models;

namespace NasaTest.Controllers
{
    public class HomeController1 : Controller
    {
   
        public HomeController1(LocationService locationService ,AiDataService aiDataService, SharkService sharkService)
		{
			this.locationService = locationService;
            this.aiDataService = aiDataService;
            _sharkService = sharkService;
        }

		OtherProperties defaultProperties = new OtherProperties()
        {
            Longitude = 1,
            Latitude = 1,
            Temperatue = 1,
            Pressure = 1,
            EatingProbability = 1

        };

        SharkEntity sharkEntity = new SharkEntity
        {
            Depth = 1,
            Temperatue = 1,
            EatingProbability = 1,
            Longitude = 1,
            Latitude = 1,
            Time = new DateTime(1, 1, 1, 1, 1, 1)


        };

		private readonly LocationService locationService;
        private readonly AiDataService aiDataService;
        private readonly SharkService _sharkService;

        [Route("home/device")]
        public async Task< IActionResult> Home()
        {

         
            if (locationService.LastProperties == null)
                return View(defaultProperties);

            



            return View(locationService.LastProperties);
        }



        [Route("home/sharks/{id}")]
        [Route("home/sharks")]
        [HttpPost]

       


        public async Task<IActionResult> SharksInfo(int id = 1)
        {


            var shark = await _sharkService.GetSharkByIdAsync(id);

            if (shark == null)
                return View(sharkEntity);





            return View(shark);
        }


        [Route("home/sharks")]
        [HttpGet]

        public async Task< IActionResult> SharksInfo()
        {


            var shark = await _sharkService.GetSharkByIdAsync(1);

            if (shark == null)
                return View(sharkEntity);





            return View(shark);




            
        }




    }
}
