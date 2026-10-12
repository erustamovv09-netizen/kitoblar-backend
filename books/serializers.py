from rest_framework import serializers
from .models import Category, Book, Review, ReadingProgress
import re

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_slug = serializers.ReadOnlyField(source='category.slug')
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = [
            'id', 'category', 'category_name', 'category_slug',
            'title', 'author', 'price', 'rating', 'description',
            'pages', 'language', 'year', 'cover_image', 'file',
            'content',
            'is_weekly_top', 'is_trending', 'created_at'
        ]

    def to_internal_value(self, data):
        try:
            if hasattr(data, '_mutable') and not data._mutable:
                data._mutable = True
            elif hasattr(data, 'copy'):
                data = data.copy()
        except Exception:
            pass

        if hasattr(data, 'get'):
            raw_year = data.get('year')
            if raw_year and isinstance(raw_year, str):
                m = re.search(r'\d{4}', raw_year)
                if m:
                    data['year'] = int(m.group(0))

        return super().to_internal_value(data)


class ReviewSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Review
        fields = ['id', 'book', 'user_name', 'user_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_comment(self, value):
        if not value or not value.strip():
            # Agar izoh yozilmagan bo'lsa, chiroyli standart matn qo'yamiz
            rating_val = self.initial_data.get('rating', 5)
            return f"{rating_val} yulduz bilan baholandi ⭐"
        return value


class ReadingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingProgress
        fields = ['id', 'book', 'user_id', 'chapter', 'chapter_index', 'progress_percent', 'updated_at']
        read_only_fields = ['id', 'updated_at']
