from django.test import TestCase
from django.test import TestCase
from django.contrib.auth.models import User
from messaging.models import Message, Notification


class MessageSignalTest(TestCase):

    def test_notification_created_on_message_send(self):
        sender = User.objects.create_user(username="sender", password="pass123")
        receiver = User.objects.create_user(username="receiver", password="pass123")

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content="Hello!"
        )

        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.user, receiver)
        self.assertEqual(notification.message, message)