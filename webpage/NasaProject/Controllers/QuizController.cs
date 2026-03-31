using Microsoft.AspNetCore.Mvc;
using NasaTest.Models;

namespace NasaTest.Controllers
{
    public class QuizController : Controller
    {

        [Route("home/quiz")]
        [HttpPost]
        public IActionResult SubmitQuiz(IFormCollection form)
        {
            var questions = QuizData.GetSharkQuiz();
            int score = 0;

            for (int i = 1; i <= questions.Count; i++)
            {
                var userAnswer = Convert.ToInt16( form[$"q{i}"]);
                if (userAnswer == questions[i - 1].Choice)
                {
                    score++;
                }
            }

            // Pass score and questions to result page
            if (score == 10)
                return View("Success");
            return View("Failed", score);
        }


        [Route("home/quiz")]
        [HttpGet]
        public IActionResult SubmitQuiz()
        {


            return View();
        }


        [Route("home/quiz/showanswers")]

        public IActionResult ShowAnswers()
        {
            var answers = QuizData.GetSharkQuiz();  

            return View(answers);
        }



    }
}
