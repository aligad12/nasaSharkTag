using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shark.InfraStructure.Models
{
    public class SharkEntity
    {

        [Key]
      public  int Id { get; set; }

        public double Longitude { get; set; }

        public double Latitude { get; set; }
        public double Temperatue { get; set; }

        public double Depth { get; set; }
        public double EatingProbability { get; set; }

        public DateTime Time { get; set; }


        

    }
}
