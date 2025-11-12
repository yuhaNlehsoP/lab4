from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    director = models.CharField(max_length=100, verbose_name="Режиссер")
    year = models.IntegerField(
        validators=[MinValueValidator(1895), MaxValueValidator(2030)],
        verbose_name="Год"
    )
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Продолжительность (мин)"
    )
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Рейтинг"
    )
    description = models.TextField(verbose_name="Описание")
    cast = models.TextField(verbose_name="В ролях")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['title', 'director', 'year']  # Проверка на дубликаты
    
    def __str__(self):
        return f"{self.title} ({self.year})"