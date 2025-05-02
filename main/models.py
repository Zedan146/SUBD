from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Client(models.Model):
    """модель клиента"""
    name = models.CharField('Имя', max_length=100)
    surname = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['surname', 'name']

    def __str__(self):
        return f'{self.surname} {self.name}'

    @property
    def full_name(self):
        return f'{self.surname} {self.name} {self.middle_name or ""}'.strip()


class Vehicle(models.Model):
    """модель транспортного средства"""
    VEHICLE_TYPES = (
        ('car', 'Автомобиль'),
        ('truck', 'Грузовик'),
        ('bike', 'Мотоцикл'),
    )

    STATUS_CHOICES = (
        ('available', 'Свободен'),
        ('in_use', 'В работе'),
    )

    type = models.CharField('Тип ТС', max_length=20, choices=VEHICLE_TYPES)
    plate_number = models.CharField('Гос. номер', max_length=20, unique=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

    def __str__(self):
        return f'{self.get_type_display()} {self.plate_number}'


class Courier(models.Model):
    """модель курьера"""
    STATUS_CHOICES = (
        ('available', 'Свободен'),
        ('delivering', 'Доставляет заказ'),
        ('off', 'Не на смене'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='courier',
        verbose_name='Пользователь'
    )
    phone = models.CharField('Телефон', max_length=20)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Транспортное средство'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='off'
    )
    current_order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_courier',
        verbose_name='Текущий заказ'
    )
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'

    def __str__(self):
        return f'{self.user.get_full_name()}'

    @property
    def full_name(self):
        return self.user.get_full_name()


class Order(models.Model):
    """модель заказа"""
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_progress', 'В процессе доставки'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )

    number = models.CharField('Номер заказа', max_length=20, unique=True, blank=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Клиент'
    )
    delivery_address = models.TextField('Адрес доставки')
    order_amount = models.DecimalField(
        'Сумма заказа',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    delivery_cost = models.DecimalField(
        'Стоимость доставки',
        max_digits=10,
        decimal_places=2,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Курьер'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Транспортное средство'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Заказ #{self.number} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        if not self.number:
            # Генерация номера заказа при создании
            last_order = Order.objects.order_by('-id').first()
            last_id = last_order.id if last_order else 0
            self.number = f"{last_id + 10000}"

        # Автоматический расчет стоимости доставки
        if not self.delivery_cost or kwargs.get('force_delivery_calc', False):
            self.calculate_delivery_cost()

        super().save(*args, **kwargs)

    def calculate_delivery_cost(self):
        """Автоматический расчет стоимости доставки"""
        if self.order_amount < 1000:
            self.delivery_cost = 100
        elif self.order_amount < 5000:
            self.delivery_cost = 500
        else:
            self.delivery_cost = 0

