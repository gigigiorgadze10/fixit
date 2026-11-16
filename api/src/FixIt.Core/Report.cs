namespace FixIt.Core;

public class Report
{
    public int Id { get; set; }
    public Guid ReporterId { get; set; }
    public int CategoryId { get; set; }
    public string Description { get; set; } = "";
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public ReportStatus Status { get; set; } = ReportStatus.New;
    public Guid? WorkerId { get; set; }
    public string? RejectReason { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
