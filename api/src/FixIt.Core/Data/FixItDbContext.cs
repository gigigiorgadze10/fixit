using Microsoft.EntityFrameworkCore;

namespace FixIt.Core.Data;

public class FixItDbContext : DbContext
{
    public FixItDbContext(DbContextOptions<FixItDbContext> options) : base(options) { }

    public DbSet<Report> Reports => Set<Report>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Report>(e =>
        {
            e.Property(r => r.Description).HasMaxLength(500).IsRequired();
            e.Property(r => r.Status).HasConversion<string>().HasMaxLength(16);
            e.HasIndex(r => new { r.ReporterId, r.CreatedAt });
        });
    }
}
