using Microsoft.EntityFrameworkCore;

namespace FixIt.Core.Data;

public class ReportRepository
{
    private readonly FixItDbContext _db;

    public ReportRepository(FixItDbContext db) => _db = db;

    public async Task AddAsync(Report report)
    {
        _db.Reports.Add(report);
        await _db.SaveChangesAsync();
    }

    // US-04: მოქალაქის განაცხადები, ახალი ზემოთ
    public Task<List<Report>> GetByReporterAsync(Guid reporterId)
    {
        return _db.Reports
            .Where(r => r.ReporterId == reporterId)
            .OrderByDescending(r => r.CreatedAt)
            .ToListAsync();
    }
}
