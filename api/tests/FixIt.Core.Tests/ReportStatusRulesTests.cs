using FixIt.Core;

namespace FixIt.Core.Tests;

public class ReportStatusRulesTests
{
    [Theory]
    [InlineData(ReportStatus.New, ReportStatus.Accepted)]
    [InlineData(ReportStatus.New, ReportStatus.Rejected)]
    [InlineData(ReportStatus.Accepted, ReportStatus.InProgress)]
    [InlineData(ReportStatus.InProgress, ReportStatus.Resolved)]
    public void Allowed_transitions(ReportStatus from, ReportStatus to)
    {
        // Act
        var result = ReportStatusRules.CanChange(from, to);

        // Assert
        Assert.True(result);
    }

    [Theory]
    [InlineData(ReportStatus.New, ReportStatus.Resolved)]
    [InlineData(ReportStatus.Accepted, ReportStatus.Rejected)]
    [InlineData(ReportStatus.InProgress, ReportStatus.Accepted)]
    [InlineData(ReportStatus.Resolved, ReportStatus.New)]
    [InlineData(ReportStatus.Rejected, ReportStatus.Accepted)]
    public void Forbidden_transitions(ReportStatus from, ReportStatus to)
    {
        // Act
        var result = ReportStatusRules.CanChange(from, to);

        // Assert
        Assert.False(result);
    }
}
