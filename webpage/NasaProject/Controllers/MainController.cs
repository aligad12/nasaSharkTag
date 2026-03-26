using Microsoft.AspNetCore.Mvc;
using NasaTest.Models;

namespace NasaTest.Controllers
{
    public class MainController : Controller
    {

      





        [Route("/")]
        [Route("home")]
        public IActionResult Index()
        {
            return View();
        }



        [Route("Aboutus")]
        public IActionResult AboutUs()
        {
            return View();
        }


        [Route("overview")]
        public IActionResult Tales()
        {
            return View();
        }



        [Route("vision")]
        public IActionResult Vision()
        {
            return View();
        }


        [Route("mission")]
        public IActionResult Mission()
        {
            return View();
        }









    }
}
