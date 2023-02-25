"""Application models."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import genre_slug_check, year_check

User = get_user_model()


class Category(models.Model):
    """Category model class."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50,
                            validators=[genre_slug_check], unique=True)

    def __str__(self):
        return "{name: '%s', slug: '%s'}" % (self.name, self.slug)


class Genre(models.Model):
    """Genre model class."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50,
                            validators=[genre_slug_check], unique=True)

    def __str__(self):
        return f"name: {self.name}, slug: {self.slug}"


class Title(models.Model):
    """Title model class."""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория",
        null=True,
    )
    name = models.CharField("Наименование произведения", max_length=256)
    year = models.IntegerField("Год создания", validators=[year_check])
    description = models.TextField("Описание", null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name='titles')

    def __str__(self):
        return self.name


class Review(models.Model):
    """Review model class."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=False,
    )
    text = models.TextField(
        verbose_name="Отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
        null=False,
    )
    score = models.IntegerField(
        verbose_name="Оценка",
        validators=[
            MaxValueValidator(
                10,
                message="Sorry, but you cannot assign rating higher then 10."),
            MinValueValidator(
                1, message="Sorry, but you cannot assign rating lower then 1")
        ],
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["author", "title_id"],
                                    name="unique review")
        ]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["pub_date"]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Comment model class."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Отзыв"
    )
    text = models.TextField(verbose_name="Комментарий")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор"
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
