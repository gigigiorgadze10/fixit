namespace FixIt.Core;

// US-09, US-10, US-11, US-12: განაცხადის მინიჭება, დაწყება, დასრულება და უარყოფა.
public class ReportService
{
    public void Assign(Report report, Guid workerId)
    {
        // სამუშაოს დაწყებამდე შეიძლება სხვა თანამშრომელზე გადანაწილება
        if (report.Status == ReportStatus.Accepted)
        {
            report.WorkerId = workerId;
            return;
        }

        ChangeStatus(report, ReportStatus.Accepted);
        report.WorkerId = workerId;
    }

    public void Start(Report report, Guid workerId)
    {
        EnsureAssignedTo(report, workerId);
        ChangeStatus(report, ReportStatus.InProgress);
    }

    public void Complete(Report report, Guid workerId, int photoCount)
    {
        EnsureAssignedTo(report, workerId);
        if (photoCount < 1)
            throw new InvalidOperationException("ატვირთეთ შესრულებული სამუშაოს ფოტო.");

        ChangeStatus(report, ReportStatus.Resolved);
    }

    public void Reject(Report report, string reason)
    {
        if (string.IsNullOrWhiteSpace(reason))
            throw new ArgumentException("მიუთითეთ უარყოფის მიზეზი.");

        ChangeStatus(report, ReportStatus.Rejected);
        report.RejectReason = reason;
    }

    private static void EnsureAssignedTo(Report report, Guid workerId)
    {
        if (report.WorkerId != workerId)
            throw new InvalidOperationException("დავალება სხვა თანამშრომელზეა მინიჭებული.");
    }

    private static void ChangeStatus(Report report, ReportStatus to)
    {
        if (!ReportStatusRules.CanChange(report.Status, to))
            throw new InvalidOperationException($"სტატუსის ცვლილება {report.Status} -> {to} დაუშვებელია.");

        report.Status = to;
    }
}
