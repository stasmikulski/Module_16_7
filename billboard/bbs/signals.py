from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import *

from datetime import datetime, timedelta
one_week_ago = datetime.today() - timedelta(days=1)


@receiver(pre_save, sender=Comment)
def comment_confirmed(sender, instance, *args, **kwargs):
    # Отправляем письмо автору комментария, о том что комментарий принят и опубликован
    if instance.confirmed:
        print('Comment CONFIRMED:')
        user = instance.commentUser
        user_email = instance.commentUser.email
        print(user, user_email)

        email = user_email

        subject = f'Your comment in post "{instance.commentPost.title}" confirmed'
        # subject = f'Ваш комментарий к статье "{instance.commentPost.title}" принят'

        text_content = (
            f'Your comment in post "{instance.commentPost.title}" confirmed\n'
            f'Заголовок: {instance.commentPost.title}\n'
            f'Ссылка на статью: http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}'
        )
        html_content = (
            f'Your comment in post "{instance.commentPost.title}" confirmed<br>'
            f'Заголовок: {instance.commentPost.title}<br>'
            f'<a href="http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}">'
            f'Ссылка на статью</a>'
        )
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@receiver(post_save, sender=Comment)
def comment_created(instance, created, **kwargs):
    # Отправляем письмо автору статьи, о том что к статье создан комментарий
    if not created:
        return
    if created:
        print('Comment CREATED:')
        user = instance.commentPost.author.authorUser
        user_email = instance.commentPost.author.authorUser.email
        print(user, user_email)

        email = user_email

        subject = f'New comment in post {instance.commentPost.title}'
        # subject = f'Новый комментарий к статье {instance.commentPost.title}'
    
        text_content = (
            f'Заголовок: {instance.commentPost.title}\n'
            f'Ссылка на статью: http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}'
        )
        html_content = (
            f'Заголовок: {instance.commentPost.title}<br>'
            f'<a href="http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}">'
            f'Ссылка на статью</a>'
        )
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


