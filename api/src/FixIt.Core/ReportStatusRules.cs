namespace FixIt.Core;

public static class ReportStatusRules
{
    public static bool CanChange(ReportStatus from, ReportStatus to)
    {
        if (from == ReportStatus.New && to == ReportStatus.Accepted) return true;
        if (from == ReportStatus.New && to == ReportStatus.Rejected) return true;
        if (from == ReportStatus.Accepted && to == ReportStatus.InProgress) return true;
        if (from == ReportStatus.InProgress && to == ReportStatus.Resolved) return true;
        return false;
    }
}
