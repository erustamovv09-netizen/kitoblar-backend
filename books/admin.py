from django.contrib import admin
from .models import Category, Book, Review, ReadingProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'rating', 'is_weekly_top', 'is_trending')
    list_filter = ('category', 'is_weekly_top', 'is_trending')
    search_fields = ('title', 'author', 'description')
    list_editable = ('price', 'rating', 'is_weekly_top', 'is_trending')

    # Tahrirlash sahifasida maydonlarni guruhlash
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'author', 'category', 'price', 'rating', 'language', 'year', 'pages')
        }),
        ('Tavsif', {
            'fields': ('description',)
        }),
        ('Kitob matni (o\'qish uchun)', {
            'fields': ('content',),
            'description': 'O\'quvchilar o\'qishi uchun kitob matnini kiriting. Boblarni ajratish uchun: --- 1-Bob: Bob nomi --- formatidan foydalaning.',
        }),
        ('Rasm va Fayl', {
            'fields': ('cover_image', 'file')
        }),
        ('Ko\'rinish sozlamalari', {
            'fields': ('is_weekly_top', 'is_trending')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user_name', 'rating', 'created_at')
    list_filter = ('book', 'rating')
    search_fields = ('user_name', 'comment')
    readonly_fields = ('created_at',)


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('book', 'user_id', 'chapter', 'progress_percent', 'updated_at')
    list_filter = ('book',)
    search_fields = ('user_id',)
    readonly_fields = ('updated_at',)
