from django.contrib import admin
from .models import Post, Comment, AuthorProfile, SiteSettings, Review, BotSubscriber

@admin.register(BotSubscriber)
class BotSubscriberAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'joined_at')

# Регистрация профиля
@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Если профиль уже создан, кнопка "Добавить" исчезнет
        return AuthorProfile.objects.count() == 0

#  Обновленная админка постов
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Добавили is_featured в список и сделали его редактируемым
    list_display = ('title', 'category', 'is_featured', 'created_at')
    list_editable = ('is_featured',)
    list_filter = ('category', 'is_featured')

#  админка комментариев
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'post', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Одобрить выбранные комментарии'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return SiteSettings.objects.count() == 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_favorite')
    list_editable = ('is_favorite',)