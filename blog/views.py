from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, AuthorProfile, SiteSettings
from django.contrib import messages
from .forms import CommentForm
from django.db.models import Count, Q
from django.core.paginator import Paginator  # <-- Импорт для пагинации
from django.conf import settings  # <-- Импорт для безопасных ключей
import requests
import threading


def send_telegram_message(text):
    # Безопасно берем ключи из настроек (settings.py -> .env)
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

    if not bot_token or not chat_id:
        print("ВНИМАНИЕ: Ключи Telegram не настроены в settings.py!")
        return

    # Формируем запрос к API Telegram
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    # Пытаемся отправить
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f'Ошибка отправки в Telegram: {e}')


# 1. ГЛАВНАЯ СТРАНИЦА
def index(request):
    settings_obj = SiteSettings.objects.first()

    def get_posts_with_count(queryset):
        return queryset.annotate(
            approved_comments_count=Count('comments',
                                          filter=Q(comments__is_approved=True))
        )

    featured_post = Post.objects.filter(is_featured=True).first()
    if not featured_post:
        featured_post = Post.objects.order_by('-created_at').first()

    if featured_post:
        featured_post = get_posts_with_count(
            Post.objects.filter(id=featured_post.id)).first()

    raw_posts = Post.objects.exclude(
        id=featured_post.id if featured_post else 0).order_by('-created_at')[:6]
    posts = get_posts_with_count(raw_posts)

    return render(request, 'blog/index.html', {
        'settings': settings_obj,
        'featured_post': featured_post,
        'posts': posts
    })


# 2. СТРАНИЦА "ОБ АВТОРЕ"
def about(request):
    author = AuthorProfile.objects.first()
    return render(request, 'blog/about.html', {'author': author})


# 3. ВСЕ ПУБЛИКАЦИИ (Архив с пагинацией)
def all_posts(request):
    # Получаем все посты с подсчетом комментов
    post_list = Post.objects.annotate(
        approved_comments_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-created_at')

    # Включаем Paginator: 4 постов на одну страницу
    paginator = Paginator(post_list, 4)

    # Получаем номер текущей страницы из URL (например, ?page=2)
    page_number = request.GET.get('page')

    # Получаем посты именно для этой страницы
    posts = paginator.get_page(page_number)

    return render(request, 'blog/all_posts.html', {'posts': posts})


# 4. СТРАНИЦА ПОСТА
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(is_approved=True, parent=None)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                comment.parent = parent_obj

            comment.save()

            message_text = (
                f"🔥 <b>Новая заявка/комментарий на сайте!</b>\n\n"
                f"<b>Статья:</b> {post.title}\n"
                f"<b>Имя:</b> {comment.author_name}\n"
                f"<b>Текст:</b> {comment.text}"
            )
            threading.Thread(target=send_telegram_message, args=(message_text,)).start()

            messages.success(request, 'Ваш отклик отправлен на модерацию. Спасибо!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })