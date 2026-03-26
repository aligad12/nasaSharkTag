using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Shark.InfraStructure.AppDbContext;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shark.InfraStructure.DesignFactory
{
    public class SharkAppFactory : IDesignTimeDbContextFactory<SharkApp>
    {
        public SharkApp CreateDbContext(string[] args)
        {
            var optionsBuilder = new DbContextOptionsBuilder<SharkApp>();

            // Replace with your actual connection string
            optionsBuilder.UseSqlServer("Server=.;Database=SharkDb;Trusted_Connection=True;TrustServerCertificate=True");

            return new SharkApp(optionsBuilder.Options);
        }

    }
}
