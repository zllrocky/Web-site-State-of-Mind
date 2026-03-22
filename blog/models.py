import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models


# 1. ОБЩАЯ ФУНКЦИЯ (Наш "завод" по переработке картинок в WebP)
def compress_image(image, size=(1200, 800)):
    if not image:
        return None

    img = Image.open(image)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Меняем размер, сохраняя пропорции
    img.thumbnail(size, Image.LANCZOS)

    output = BytesIO()
    # Сохраняем в самом современном формате с качеством 75%
    img.save(output, format='WebP', quality=80, method=6)
    output.seek(0)

    # Формируем файл для Django с расширением .webp
    return InMemoryUploadedFile(
        output, 'ImageField', f"{image.name.split('.')[0]}.webp",
        'image/webp', sys.getsizeof(output), None
    )


# 2. МОДЕЛЬ ПОСТА
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('THOUGHTS', 'Мысли'),
        ('TECHNIQUE', 'Техники'),
        ('CASE', 'Кейсы'),
    ]

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст статьи')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,
                                default='THOUGHTS', verbose_name='Категория')
    image = models.ImageField(upload_to='blog_photos/', blank=True, null=True,
                              verbose_name='Главное фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_featured = models.BooleanField(default=False, verbose_name="Главный пост (Hero)")

    def save(self, *args, **kwargs):
        # Если загрузили новую картинку и это не webp — жмём
        if self.image and not self.image.name.endswith('.webp'):
            self.image = compress_image(self.image, size=(1200, 1200))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# 3. МОДЕЛЬ АВТОРА
class AuthorProfile(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя автора')
    bio = models.TextField(verbose_name='О себе')
    photo = models.ImageField(upload_to='profile/', verbose_name='Фото профиля')

    def save(self, *args, **kwargs):
        if self.photo and not self.photo.name.endswith('.webp'):
            self.photo = compress_image(self.photo, size=(1500, 1500))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Профиль автора'
        verbose_name_plural = 'Профиль автора'

    def __str__(self):
        return self.name

# 4. МОДЕЛЬ КОММЕНТАРИЕВ
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100, verbose_name='Имя автора')
    text = models.TextField(verbose_name='Комментарий')
    is_approved = models.BooleanField(default=False,
                                      verbose_name='Одобрено модератором')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'От {self.author_name} к посту {self.post.title}'


# 5. МОДЕЛЬ НАСТРОЕК САЙТА
class SiteSettings(models.Model):
    hero_title = models.CharField(max_length=100, default="STATE OF MIND",
                                  verbose_name="Заголовок на главной")
    hero_subtitle = models.CharField(max_length=100,
                                     default="Editorial & Coaching by Julia",
                                     verbose_name="Подзаголовок")
    hero_image = models.ImageField(upload_to='settings/',
                                   verbose_name="Главное фото (Hero)")

    def save(self, *args, **kwargs):
        # Фоновое фото Hero жмём до 1920px (FullHD)
        if self.hero_image and not self.hero_image.name.endswith('.webp'):
            self.hero_image = compress_image(self.hero_image, size=(1920, 1080))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки оформления"

class Review(models.Model):
    image = models.ImageField("Скриншот отзыва", upload_to='reviews/')
    is_favorite = models.BooleanField("Показывать в карусели", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.created_at.strftime('%d.%m.%Y')}"