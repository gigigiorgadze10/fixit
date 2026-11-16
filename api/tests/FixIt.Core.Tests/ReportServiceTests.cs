using FixIt.Core;

namespace FixIt.Core.Tests;

public class ReportServiceTests
{
    private readonly ReportService _service = new();
    private readonly Guid _worker = Guid.NewGuid();

    [Fact]
    public void Assign_new_report_makes_it_accepted()
    {
        // Arrange
        var report = new Report();

        // Act
        _service.Assign(report, _worker);

        // Assert
        Assert.Equal(ReportStatus.Accepted, report.Status);
        Assert.Equal(_worker, report.WorkerId);
    }

    [Fact]
    public void Accepted_report_can_be_reassigned_before_work_starts()
    {
        // Arrange
        var report = new Report { Status = ReportStatus.Accepted, WorkerId = _worker };
        var otherWorker = Guid.NewGuid();

        // Act
        _service.Assign(report, otherWorker);

        // Assert
        Assert.Equal(otherWorker, report.WorkerId);
        Assert.Equal(ReportStatus.Accepted, report.Status);
    }

    [Fact]
    public void Report_in_progress_cannot_be_reassigned()
    {
        // Arrange
        var report = new Report { Status = ReportStatus.InProgress, WorkerId = _worker };

        // Act + Assert
        Assert.Throws<InvalidOperationException>(() => _service.Assign(report, Guid.NewGuid()));
    }

    [Fact]
    public void Other_worker_cannot_start_the_task()
    {
        // Arrange
        var report = new Report { Status = ReportStatus.Accepted, WorkerId = _worker };

        // Act + Assert
        Assert.Throws<InvalidOperationException>(() => _service.Start(report, Guid.NewGuid()));
        Assert.Equal(ReportStatus.Accepted, report.Status);
    }

    [Fact]
    public void Complete_without_photo_is_blocked()
    {
        // Arrange
        var report = new Report { Status = ReportStatus.InProgress, WorkerId = _worker };

        // Act
        var ex = Assert.Throws<InvalidOperationException>(() => _service.Complete(report, _worker, photoCount: 0));

        // Assert
        Assert.Equal("ატვირთეთ შესრულებული სამუშაოს ფოტო.", ex.Message);
        Assert.Equal(ReportStatus.InProgress, report.Status);
    }

    [Fact]
    public void Full_flow_ends_with_resolved()
    {
        // Arrange
        var report = new Report();

        // Act
        _service.Assign(report, _worker);
        _service.Start(report, _worker);
        _service.Complete(report, _worker, photoCount: 1);

        // Assert
        Assert.Equal(ReportStatus.Resolved, report.Status);
    }
}
