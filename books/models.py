from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug (URL uchun, masalan: badiiy)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="books", verbose_name="Kategoriyasi")
    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, verbose_name="Muallif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi (so'mda)")
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="Reyting (0 dan 5 gacha)"
    )
    description = models.TextField(verbose_name="Kitob haqida (Tavsif)")
    pages = models.PositiveIntegerField(verbose_name="Sahifalar soni")
    language = models.CharField(max_length=50, default="O'zbek tili", verbose_name="Tili")
    year = models.PositiveIntegerField(verbose_name="Chop etilgan yili")

    # Kitob matni — o'qish uchun
    content = models.TextField(blank=True, default='', verbose_name="Kitob matni (o'qish uchun)")

    # Rasmlar va Fayllar uchun
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True, verbose_name="Muqova rasmi")
    file = models.FileField(upload_to="book_files/", blank=True, null=True, verbose_name="Kitob fayli (PDF/EPUB)")

    is_weekly_top = models.BooleanField(default=False, verbose_name="Hafta kitobi (Katta banner uchun)")
    is_trending = models.BooleanField(default=True, verbose_name="Trenddagi kitob (Asosiy sahifa uchun)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-created_at']


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="Kitob")
    user_name = models.CharField(max_length=100, default="Foydalanuvchi", verbose_name="Foydalanuvchi ismi")
    user_id = models.CharField(max_length=100, blank=True, default='', verbose_name="Foydalanuvchi ID")
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="Baho (0-5)"
    )
    comment = models.TextField(blank=True, default="", verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan vaqt")

    def __str__(self):
        return f"{self.user_name} — {self.book.title} ({self.rating})"

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ['-created_at']


class ReadingProgress(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="progress", verbose_name="Kitob")
    user_id = models.CharField(max_length=100, verbose_name="Foydalanuvchi ID")
    chapter = models.CharField(max_length=255, blank=True, default='', verbose_name="Bob nomi")
    chapter_index = models.IntegerField(default=0, verbose_name="Bob indeksi")
    progress_percent = models.FloatField(default=0.0, verbose_name="O'qilgan foiz (%)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    def __str__(self):
        return f"{self.user_id} — {self.book.title} ({self.progress_percent}%)"

    class Meta:
        verbose_name = "O'qish jarayoni"
        verbose_name_plural = "O'qish jarayonlari"
        unique_together = ('book', 'user_id')
