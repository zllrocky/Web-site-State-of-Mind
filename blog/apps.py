from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    # Вот эта магия запускает рассылку:
    def ready(self):
        import blog.signals