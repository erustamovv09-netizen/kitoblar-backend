from rest_framework import viewsets, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Book, Review, ReadingProgress
from .serializers import CategorySerializer, BookSerializer, ReviewSerializer, ReadingProgressSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kategoriyalarni ko'rish uchun API endpoint (/api/categories/)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    Kitoblarni ko'rish, qo'shish, tahrirlash va o'chirish (/api/books/)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        queryset = Book.objects.all()

        category_slug = self.request.query_params.get('category', None)
        is_trending = self.request.query_params.get('is_trending', None)
        is_weekly_top = self.request.query_params.get('is_weekly_top', None)

        if category_slug is not None:
            queryset = queryset.filter(category__slug=category_slug)

        if is_trending is not None:
            queryset = queryset.filter(is_trending=is_trending.lower() == 'true')

        if is_weekly_top is not None:
            queryset = queryset.filter(is_weekly_top=is_weekly_top.lower() == 'true')

        return queryset

    # ── GET/POST /api/books/{id}/reviews/ ──────────────────────────
    @action(detail=True, methods=['get', 'post'], url_path='reviews')
    def reviews(self, request, pk=None):
        book = self.get_object()

        if request.method == 'GET':
            reviews = Review.objects.filter(book=book)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            data = request.data.copy()
            data['book'] = book.id
            serializer = ReviewSerializer(data=data)
            if serializer.is_valid():
                serializer.save(book=book)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── GET/POST /api/books/{id}/progress/ ─────────────────────────
    @action(detail=True, methods=['get', 'post'], url_path='progress')
    def progress(self, request, pk=None):
        book = self.get_object()
        user_id = request.data.get('userId') or request.query_params.get('userId', 'anonymous')

        if request.method == 'GET':
            try:
                prog = ReadingProgress.objects.get(book=book, user_id=user_id)
                serializer = ReadingProgressSerializer(prog)
                return Response(serializer.data)
            except ReadingProgress.DoesNotExist:
                return Response(None, status=status.HTTP_200_OK)

        if request.method == 'POST':
            chapter = request.data.get('chapter', '')
            chapter_index = request.data.get('chapterIndex', 0)
            progress_percent = request.data.get('progressPercent', 0.0)

            prog, created = ReadingProgress.objects.update_or_create(
                book=book,
                user_id=user_id,
                defaults={
                    'chapter': chapter,
                    'chapter_index': chapter_index,
                    'progress_percent': progress_percent,
                }
            )
            serializer = ReadingProgressSerializer(prog)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)


from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta


class AdminStatsView(APIView):
    """
    Admin panel uchun umumiy statistika: /api/admin/stats/
    """
    def get(self, request):
        total_books = Book.objects.count()
        total_reviews = Review.objects.count()
        total_progress = ReadingProgress.objects.count()
        total_users = User.objects.count()
        avg_rating = Book.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        # So'nggi 7 kunda qo'shilgan kitoblar
        week_ago = timezone.now() - timedelta(days=7)
        new_books_week = Book.objects.filter(created_at__gte=week_ago).count()

        # Kategoriyalar bo'yicha statistika
        categories = list(
            Book.objects.values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Eng ko'p o'qilgan kitoblar (progress soni bo'yicha)
        top_books = list(
            ReadingProgress.objects
            .values('book__id', 'book__title', 'book__author')
            .annotate(readers=Count('user_id'))
            .order_by('-readers')[:5]
        )

        # So'nggi sharhlar
        recent_reviews = list(
            Review.objects
            .select_related('book')
            .order_by('-created_at')[:5]
            .values('id', 'user_name', 'rating', 'comment', 'created_at', 'book__title')
        )

        # So'nggi foydalanuvchilar
        recent_users = list(
            User.objects
            .order_by('-date_joined')[:200]
            .values('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_active')
        )

        # Foydalanuvchilar o'qish jarayoni va kitoblari
        user_progress = list(
            ReadingProgress.objects
            .select_related('book')
            .order_by('-updated_at')
            .values(
                'id',
                'user_id',
                'book__id',
                'book__title',
                'book__author',
                'book__cover_image',
                'chapter',
                'chapter_index',
                'progress_percent',
                'updated_at'
            )
        )

        return Response({
            'total_books': total_books,
            'total_reviews': total_reviews,
            'total_progress': total_progress,
            'total_users': total_users,
            'avg_rating': round(avg_rating, 2),
            'new_books_week': new_books_week,
            'categories': categories,
            'top_books': top_books,
            'recent_reviews': recent_reviews,
            'recent_users': recent_users,
            'user_progress': user_progress,
        })

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            # Update last_login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Use Token or just return success
            # token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.first_name,
            })
        else:
            return Response({'error': 'Login yoki parol xato!'}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name', '')
        
        if not username or not password:
            return Response({'error': 'Username va parol shart!'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Bu username band.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.first_name,
        })

class PingView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                return Response({'status': 'ok'})
        return Response({'status': 'ignored'})
