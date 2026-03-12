from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, AuthorProfile, SiteSettings
from django.contrib import messages
from .forms import CommentForm
from django.db.models import Count, Q
import requests
import threading


def send_telegram_message(text):
    # Мои доступы
    bot_token = '8649090518:AAHTvHzzz3nzR0_Tgidfqhkrr8ugaAtyEFs'
    chat_id = '402091251'

    # Формируем запрос к API Telegram
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    # Пытаемся отправить (и не роняем сайт, если телега тупит)
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f'Ошибка отправки в Telegram: {e}')


# 1. ГЛАВНАЯ СТРАНИЦА (Только Hero и Карусель)
def index(request):
    settings = SiteSettings.objects.first()

    # Считаем только ОДОБРЕННЫЕ комментарии для каждого поста
    def get_posts_with_count(queryset):
        return queryset.annotate(
            approved_comments_count=Count('comments', filter=Q(comments__is_approved=True))
        )

    # Главный пост
    featured_post = Post.objects.filter(is_featured=True).first()
    if not featured_post:
        featured_post = Post.objects.order_by('-created_at').first()

    if featured_post:
        # Добавляем счетчик к главному посту
        featured_post = get_posts_with_count(Post.objects.filter(id=featured_post.id)).first()

    # Посты для карусели
    raw_posts = Post.objects.exclude(id=featured_post.id).order_by('-created_at')[:6]
    posts = get_posts_with_count(raw_posts)

    return render(request, 'blog/index.html', {
        'settings': settings,
        'featured_post': featured_post,
        'posts': posts
    })


# 2. СТРАНИЦА "ОБ АВТОРЕ"
def about(request):
    author = AuthorProfile.objects.first()
    return render(request, 'blog/about.html', {'author': author})


# 3. ВСЕ ПУБЛИКАЦИИ (Архив/Галерея)
def all_posts(request):
    # Добавляем подсчет одобренных комментариев
    posts = Post.objects.annotate(
        approved_comments_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-created_at')

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

            # 1. Сохраняем в базу данных
            comment.save()

            # 2. Отправляем уведомление
            message_text = (
                f"🔥 <b>Новая заявка/комментарий на сайте!</b>\n\n"
                f"<b>Статья:</b> {post.title}\n"
                f"<b>Имя:</b> {comment.author_name}\n"
                f"<b>Текст:</b> {comment.text}"
            )
            threading.Thread(target=send_telegram_message, args=(message_text,)).start()

            # 3. Показываем сообщение об успехе и перезагружаем страницу
            messages.success(request, 'Ваш отклик отправлен на модерацию. Спасибо!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })