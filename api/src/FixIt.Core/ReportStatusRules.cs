namespace FixIt.Core;

// დაშვებული სტატუსის ცვლილებები ერთ ადგილას.
public static class ReportStatusRules
{
    private static readonly Dictionary<ReportStatus, ReportStatus[]> Allowed = new()
    {
        [ReportStatus.New] = new[] { ReportStatus.Accepted, ReportStatus.Rejected },
        [ReportStatus.Accepted] = new[] { ReportStatus.InProgress },
        [ReportStatus.InProgress] = new[] { ReportStatus.Resolved },
    };

    public static bool CanChange(ReportStatus from, ReportStatus to)
    {
        return Allowed.TryGetValue(from, out var next) && next.Contains(to);
    }
}
