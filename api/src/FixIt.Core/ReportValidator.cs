namespace FixIt.Core;

// US-02 და US-03: განაცხადის შემოწმება შენახვამდე.
public static class ReportValidator
{
    public const int MinDescriptionLength = 10;
    public const int MaxDescriptionLength = 500;
    public const int MaxPhotos = 3;
    public const long MaxPhotoBytes = 10 * 1024 * 1024;

    private static readonly string[] AllowedTypes = { "image/jpeg", "image/png" };

    public static List<string> Validate(string? description, IReadOnlyList<PhotoInfo> photos, double latitude, double longitude)
    {
        var errors = new List<string>();

        var length = description?.Trim().Length ?? 0;
        if (length < MinDescriptionLength || length > MaxDescriptionLength)
            errors.Add("აღწერა უნდა იყოს 10-500 სიმბოლო.");

        if (photos.Count == 0 || photos.Count > MaxPhotos)
            errors.Add("საჭიროა 1-3 ფოტო.");

        foreach (var photo in photos)
        {
            if (photo.SizeBytes > MaxPhotoBytes)
                errors.Add("ფოტო 10 MB-ზე დიდია.");
            if (!AllowedTypes.Contains(photo.ContentType))
                errors.Add("დასაშვებია მხოლოდ JPEG და PNG.");
        }

        if (latitude is < -90 or > 90 || longitude is < -180 or > 180)
            errors.Add("კოორდინატები არასწორია.");

        return errors;
    }
}
