using Microsoft.EntityFrameworkCore;
using Shark.InfraStructure.AppDbContext;
using Shark.InfraStructure.Models;

namespace NasaTest.Services
{
    public class SharkService
    {
        private readonly SharkApp _sharkApp;

        public SharkService(SharkApp sharkApp)
        {
            _sharkApp = sharkApp;
        }

        // ✅ Add
        public async Task<int> AddShark(SharkEntity? shark)
        {
            if (shark == null) return 0;

            await _sharkApp.AddAsync(shark);
            await _sharkApp.SaveChangesAsync();
            return 1;
        }

        // ✅ Update
        public async Task<int> UpdateSharkAsync(SharkEntity? shark)
        {
            if (shark == null) return 0;

            var sharkReal = await _sharkApp.Set<SharkEntity>().FindAsync(shark.Id);
            if (sharkReal == null) return 0;

            sharkReal.Depth = shark.Depth;
            sharkReal.Temperatue = shark.Temperatue;
            sharkReal.Longitude = shark.Longitude;
            sharkReal.Latitude = shark.Latitude;
            sharkReal.EatingProbability = shark.EatingProbability;
            sharkReal.Time = shark.Time;

            await _sharkApp.SaveChangesAsync();
            return 1;
        }

        // ✅ Get by Id
        public async Task<SharkEntity?> GetSharkByIdAsync(int id)
        {
            return await _sharkApp.Set<SharkEntity>().FindAsync(id);
        }

        // ✅ Get All
        public async Task<IEnumerable<SharkEntity>> GetAllSharksAsync()
        {
            return await _sharkApp.Set<SharkEntity>().ToListAsync();
        }

        // ✅ Delete
        public async Task<int> DeleteAsync(int id)
        {
            var shark = await _sharkApp.Set<SharkEntity>().FindAsync(id);
            if (shark == null) return 0;

            _sharkApp.Remove(shark);
            await _sharkApp.SaveChangesAsync();
            return 1;
        }
    }
}
