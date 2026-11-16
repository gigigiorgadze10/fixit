using FixIt.Core.Data;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace FixIt.Core.Tests;

// Integration ტესტი: რეალური SQLite ბაზა მეხსიერებაში.
public class ReportRepositoryTests : IDisposable
{
    private readonly SqliteConnection _connection;
    private readonly FixItDbContext _db;

    public ReportRepositoryTests()
    {
        _connection = new SqliteConnection("DataSource=:memory:");
        _connection.Open();
        var options = new DbContextOptionsBuilder<FixItDbContext>().UseSqlite(_connection).Options;
        _db = new FixItDbContext(options);
        _db.Database.EnsureCreated();
    }

    [Fact]
    public async Task Citizen_sees_only_own_reports_newest_first()
    {
        // Arrange
        var me = Guid.NewGuid();
        var someoneElse = Guid.NewGuid();
        var repo = new ReportRepository(_db);
        await repo.AddAsync(new Report { ReporterId = me, Description = "ძველი განაცხადი", CreatedAt = new DateTime(2026, 12, 1) });
        await repo.AddAsync(new Report { ReporterId = me, Description = "ახალი განაცხადი", CreatedAt = new DateTime(2026, 12, 5) });
        await repo.AddAsync(new Report { ReporterId = someoneElse, Description = "სხვისი განაცხადი" });

        // Act
        var result = await repo.GetByReporterAsync(me);

        // Assert
        Assert.Equal(2, result.Count);
        Assert.Equal("ახალი განაცხადი", result[0].Description);
        Assert.All(result, r => Assert.Equal(me, r.ReporterId));
    }

    [Fact]
    public async Task Status_is_saved_and_read_back()
    {
        // Arrange
        var me = Guid.NewGuid();
        var repo = new ReportRepository(_db);
        await repo.AddAsync(new Report { ReporterId = me, Description = "ორმო გზაზე", Status = ReportStatus.Accepted });
        _db.ChangeTracker.Clear();

        // Act
        var saved = (await repo.GetByReporterAsync(me)).Single();

        // Assert
        Assert.Equal(ReportStatus.Accepted, saved.Status);
    }

    public void Dispose()
    {
        _db.Dispose();
        _connection.Dispose();
    }
}
