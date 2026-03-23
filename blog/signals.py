import os
import requests
from dotenv import load_dotenv  # Добавили импорт
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, BotSubscriber

# Загружаем переменные из .env
load_dotenv()


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:  # Сработает только при создании нового поста
        token = os.getenv('BOT_TOKEN')
        subscribers = BotSubscriber.objects.all()

        # Ссылка на пост
        url = f"https://www.stateofmind-space.com/post/{instance.id}/"
        text = f"🌿 Новый пост в State of Mind:\n\n{instance.title}\n\nЧитать тут: {url}"

        for sub in subscribers:
            try:
                # Добавили timeout, чтобы сайт не "висел", если Телеграм долго отвечает
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": sub.chat_id, "text": text},
                    timeout=5
                )
            except Exception as e:
                # Если одному юзеру не отправилось, код не упадет и пойдет дальше
                print(f"Ошибка отправки для {sub.chat_id}: {e}")