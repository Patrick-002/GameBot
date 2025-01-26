from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        user = self.create_user(username, password, **extra_fields)
        return user


class Game(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Название игры")
    description = models.TextField(verbose_name="Описание игры")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    release_date = models.DateField(null=True, blank=True, verbose_name="Дата выпуска")

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):
    email = None
    is_superuser = None
    first_name = None
    last_name = None

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Указываем, какое поле будет использоваться для уникальной идентификации
    USERNAME_FIELD = 'username'
    # Поля, которые запрашиваются при создании пользователя через manage.py
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="purchases",
                             verbose_name="Пользователь")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="purchases", verbose_name="Игра")
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата покупки")

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"
