from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

# Валидация логина
login_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message='Логин может содержать только латинские буквы и цифры.',
)
# Валидация номера телефона
phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message='Введите телефон в формате +79991234567 или 89991234567.',
)


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField('Электронная почта', unique=True)
    full_name = models.CharField('ФИО', max_length=255)
    phone = models.CharField('Телефон', max_length=16, validators=[phone_validator])
    username = models.CharField('Логин', max_length=150, unique=True, validators=[login_validator],)
    REQUIRED_FIELDS = ['email', 'full_name', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name or self.username


class Venue(models.Model):
    name = models.CharField('Название помещения', max_length=150)
    location = models.CharField('Расположение', max_length=200)
    capacity = models.PositiveIntegerField('Вместимость')
    hourly_rate = models.DecimalField('Стоимость в час', max_digits=10, decimal_places=2)
    short_description = models.TextField('Краткое описание')
    amenities = models.TextField('Удобства')
    image = models.CharField('Изображение', max_length=255,)
    display_order = models.PositiveIntegerField('Порядок показа', default=0)

    class Meta:
        ordering = ('display_order', 'name')
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'

    def __str__(self):
        return self.name

    @property
    def amenities_list(self):
        return [item.strip() for item in self.amenities.split(',') if item.strip()]


class BookingRequest(models.Model):
    class PaymentMethod(models.TextChoices):
        CARD = 'card', 'Предоплата по QR-коду'
        CASH = 'cash', 'Постоплата в офисе организации'
        INVOICE = 'invoice', 'Оплата картой МИР'
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        SCHEDULED = 'scheduled', 'Мероприятие назначено'
        COMPLETED = 'completed', 'Мероприятие завершено'

    user = models.ForeignKey('conference.User', on_delete=models.CASCADE, related_name="booking_requests", verbose_name="Пользователь")
    venue = models.ForeignKey(Venue,on_delete=models.PROTECT, related_name='booking_requests', verbose_name='Помещение')
    conference_title = models.CharField('Название мероприятия', max_length=200)
    event_date = models.DateField('Дата проведения')
    preferred_time = models.TimeField('Предпочтительное время')
    attendees = models.PositiveIntegerField('Количество участников', default=10)
    payment_method = models.CharField('Способ оплаты', choices=PaymentMethod.choices,default=PaymentMethod.CARD, max_length=30)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    special_requests = models.TextField('Комментарий к заявке', blank=True)
    admin_comment = models.TextField('Комментарий администратора', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'{self.conference_title} - {self.venue.name}'

    def clean(self):
        if self.event_date and self.event_date < timezone.localdate():
            raise ValidationError({'event_date': 'Дата бронирования не может быть в прошлом.'})

        if self.attendees and self.venue_id and self.attendees > self.venue.capacity:
            raise ValidationError(
                {'attendees': f'Для этой площадки доступно максимум {self.venue.capacity} гостей.'}
            )

    @property
    def can_leave_review(self):
        return self.status != self.Status.NEW and not hasattr(self, 'review')

    @property
    def status_badge_class(self):
        return {
            self.Status.NEW: 'badge badge-new',
            self.Status.SCHEDULED: 'badge badge-scheduled',
            self.Status.COMPLETED: 'badge badge-completed',
        }.get(self.status, 'badge')


class Review(models.Model):
    booking_request = models.OneToOneField(BookingRequest, on_delete=models.CASCADE, related_name='review', verbose_name='Заявка')
    user = models.ForeignKey('conference.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='Автор',)
    rating = models.PositiveSmallIntegerField('Оценка')
    comment = models.TextField('Отзыв')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв {self.user} ({self.rating}/5)'

    def clean(self):
        if self.booking_request.user_id != self.user_id:
            raise ValidationError('Отзыв может оставить только владелец заявки.')
        if self.booking_request.status == BookingRequest.Status.NEW:
            raise ValidationError('Оставить отзыв можно только после изменения статуса заявки.')
