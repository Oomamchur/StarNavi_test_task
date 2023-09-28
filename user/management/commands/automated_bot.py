import configparser
import random
import uuid

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from user.models import Post, Like

config = configparser.ConfigParser()
config.read("config.ini")

NUMBER_OF_USERS = config.getint("DEFAULT", "number_of_users")
MAX_POSTS_PER_USER = config.getint("DEFAULT", "max_posts_per_user")
MAX_LIKES_PER_USER = config.getint("DEFAULT", "max_likes_per_user")


class Command(BaseCommand):
    def handle(self, *args, **kwargs) -> None:
        for _ in range(NUMBER_OF_USERS):
            num_posts = random.randint(1, MAX_POSTS_PER_USER)
            num_likes = random.randint(1, MAX_LIKES_PER_USER)

            name = str(uuid.uuid4()).split("-")[0]

            user = get_user_model().objects.create_user(
                username=f"username-{name}",
                email=f"user-{name}@user.com",
                password="user1234",
                first_name=f"user-{name}_first_name",
                last_name=f"user-{name}_last_name",
            )

            for _ in range(num_posts):
                Post.objects.create(text="Some text", user=user)

            posts = Post.objects.all()
            liked_posts = random.choices(posts, k=num_likes)
            for liked_post in liked_posts:
                Like.objects.create(user=user, post=liked_post)

            self.stdout.write(
                f"User with {num_posts}posts and {num_likes}likes created"
            )
