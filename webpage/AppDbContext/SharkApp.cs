using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Shark.InfraStructure.Models;
using Microsoft.Identity.Client;

namespace Shark.InfraStructure.AppDbContext
{
    public class SharkApp : DbContext
    {

        public SharkApp(DbContextOptions<SharkApp> options) : base(options) {

           
       
    }

        public DbSet<SharkEntity> sharks { get; set; }


        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<SharkEntity>().ToTable("Sharks").HasKey("Id");


           
                


        }
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            base.OnConfiguring(optionsBuilder);

            optionsBuilder.UseSqlServer("Server = WIN-C3068R9C0TL\\SQLEXPRESS; Database = SharkDB; Trusted_Connection = True; TrustServerCertificate = True;");
        }








    }
}
