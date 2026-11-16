using FixIt.Core;

namespace FixIt.Core.Tests;

public class ReportValidatorTests
{
    private static readonly PhotoInfo Jpeg = new("image/jpeg", 2_000_000);

    [Fact]
    public void Valid_report_has_no_errors()
    {
        // Arrange
        var photos = new[] { Jpeg };

        // Act
        var errors = ReportValidator.Validate("ქუჩის ნათურა არ ანათებს", photos, 41.7151, 44.8271);

        // Assert
        Assert.Empty(errors);
    }

    [Theory]
    [InlineData(9, false)]
    [InlineData(10, true)]
    [InlineData(500, true)]
    [InlineData(501, false)]
    public void Description_length_limits(int length, bool isValid)
    {
        // Arrange
        var description = new string('ა', length);

        // Act
        var errors = ReportValidator.Validate(description, new[] { Jpeg }, 41.7, 44.8);

        // Assert
        Assert.Equal(isValid, errors.Count == 0);
    }

    [Theory]
    [InlineData(0, false)]
    [InlineData(1, true)]
    [InlineData(3, true)]
    [InlineData(4, false)]
    public void Photo_count_limits(int count, bool isValid)
    {
        // Arrange
        var photos = Enumerable.Repeat(Jpeg, count).ToList();

        // Act
        var errors = ReportValidator.Validate("ორმო გზაზე, სკოლის წინ", photos, 41.7, 44.8);

        // Assert
        Assert.Equal(isValid, errors.Count == 0);
    }

    [Fact]
    public void Photo_of_exactly_10_MB_is_allowed_but_one_byte_more_is_not()
    {
        // Arrange
        var exact = new PhotoInfo("image/png", ReportValidator.MaxPhotoBytes);
        var tooBig = new PhotoInfo("image/png", ReportValidator.MaxPhotoBytes + 1);

        // Act
        var exactErrors = ReportValidator.Validate("ნაგავი არ გაუტანიათ", new[] { exact }, 41.7, 44.8);
        var bigErrors = ReportValidator.Validate("ნაგავი არ გაუტანიათ", new[] { tooBig }, 41.7, 44.8);

        // Assert
        Assert.Empty(exactErrors);
        Assert.Contains("ფოტო 10 MB-ზე დიდია.", bigErrors);
    }

    [Fact]
    public void Gif_is_not_allowed()
    {
        // Arrange
        var gif = new PhotoInfo("image/gif", 1000);

        // Act
        var errors = ReportValidator.Validate("ნაგავი არ გაუტანიათ", new[] { gif }, 41.7, 44.8);

        // Assert
        Assert.Contains("დასაშვებია მხოლოდ JPEG და PNG.", errors);
    }

    [Theory]
    [InlineData(90.0, 180.0, true)]
    [InlineData(90.1, 44.8, false)]
    [InlineData(41.7, -180.1, false)]
    public void Coordinates_must_be_in_range(double lat, double lng, bool isValid)
    {
        // Act
        var errors = ReportValidator.Validate("ორმო გზაზე, სკოლის წინ", new[] { Jpeg }, lat, lng);

        // Assert
        Assert.Equal(isValid, errors.Count == 0);
    }
}
