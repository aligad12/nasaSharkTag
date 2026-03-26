namespace NasaTest.Models
{
    public class QuizData
    {
        public static List<Question> GetSharkQuiz()
        {
            return new List<Question>
            {
                new Question
                {
                    question = "1. Contrary to their reputation as lone hunters, some sharks are actually social creatures. Which of these is a known heartwarming shark behavior?",
                    Choice = 2,
                    Answer = "They can form friendships and prefer to hang out with specific individuals.",
                    Explanation = "Studies on species like lemon sharks have shown they can form complex social bonds, build 'friendships,' and return to the same groups year after year."
                },
                new Question
                {
                    question = "2. Sharks have a 'sixth sense' that feels like a superpower, allowing them to detect the faint electric fields of living things. What is this incredible sense called?",
                    Choice = 2,
                    Answer = "The Ampullae of Lorenzini",
                    Explanation = "Sharks have a network of jelly-filled pores on their snouts called the Ampullae of Lorenzini, which allows them to detect tiny electrical pulses from hidden prey."
                },
                new Question
                {
                    question = "3. Sharks are often feared as a major threat to humans. But how does the danger compare the other way around?",
                    Choice = 3,
                    Answer = "For every 1 human killed by a shark, humans kill over 10 million sharks.",
                    Explanation = "Humans kill an estimated 80-100 million sharks annually, whereas fatal shark attacks on humans are about 5-10 per year."
                },
                new Question
                {
                    question = "4. Sharks are often called the 'doctors of the sea.' Why have they earned this important title?",
                    Choice = 3,
                    Answer = "They primarily eat sick, weak, or old fish.",
                    Explanation = "By preying on the weakest individuals, sharks keep fish populations healthy and prevent disease spread."
                },
                new Question
                {
                    question = "5. How do these ancient guardians of the deep help us in the fight against climate change?",
                    Choice = 2,
                    Answer = "They protect seagrass meadows that store huge amounts of carbon.",
                    Explanation = "Sharks manage herbivore populations like sea turtles, preventing overgrazing of seagrass, which are important carbon sinks."
                },
                new Question
                {
                    question = "6. What is the single BIGGEST threat causing the catastrophic decline in shark populations today?",
                    Choice = 3,
                    Answer = "Overfishing and being accidentally caught in fishing nets (bycatch).",
                    Explanation = "Industrial overfishing and bycatch are the overwhelming causes of shark population decline."
                },
                new Question
                {
                    question = "7. Just how serious is the decline? Since 1970, the global population of oceanic sharks has fallen by a devastating...",
                    Choice = 4,
                    Answer = "71%",
                    Explanation = "Since 1970, global oceanic shark populations have fallen by 71%, showing a planetary emergency."
                },
                new Question
                {
                    question = "8. To appreciate their importance, it helps to know how long sharks have been around. Sharks are older than...",
                    Choice = 4,
                    Answer = "All of the above",
                    Explanation = "Sharks appeared over 400 million years ago, before dinosaurs and trees, and have survived multiple mass extinctions."
                },
                new Question
                {
                    question = "9. Many people think sharks just lay eggs and leave. What is a heartwarming fact about shark motherhood?",
                    Choice = 2,
                    Answer = "Some shark species give live birth, just like mammals.",
                    Explanation = "Many sharks are viviparous; some develop a placental link to nourish their pups, similar to humans."
                },
                new Question
                {
                    question = "10. Knowing all this, what is a key feature of a truly effective, modern plan to protect sharks?",
                    Choice = 2,
                    Answer = "Creating dynamic, intelligent sanctuaries that can move based on real-time data of where sharks are feeding and migrating.",
                    Explanation = "Sharks are migratory, so dynamic protected areas are more effective than static ones."
                }
            };
        }
    }
}
