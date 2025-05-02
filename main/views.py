from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import OrderForm
from .models import Order, Courier, Vehicle


def index(request):
    """Главная страница логиста"""
    # Получаем все заказы с клиентами и курьерами
    orders = Order.objects.select_related('client', 'courier', 'vehicle').all()

    # Получаем активных курьеров (на смене)
    active_couriers = Courier.objects.filter(is_active=True).select_related('user', 'vehicle')

    # Получаем все транспортные средства
    vehicles = Vehicle.objects.all()

    status_filter = request.GET.get('status', None)

    orders = Order.objects.select_related('client', 'courier', 'vehicle')

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'current_status_filter': status_filter,
        'couriers': active_couriers,
        'vehicles': vehicles,
    }

    return render(request, 'main/logist.html', context)


def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(
        Order.objects.select_related('client', 'courier', 'vehicle'),
        pk=order_id
    )
    available_couriers = Courier.objects.filter(
        is_active=True,
        status='available'
    ).exclude(
        id=order.courier.id if order.courier else None
    )

    context = {
        'order': order,
        'available_couriers': available_couriers,
    }
    return render(request, 'main/order_detail.html', context)


def assign_courier(request, order_id):
    """Назначение курьера на заказ"""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        courier_id = request.POST.get('courier_id')

        if courier_id:
            courier = get_object_or_404(Courier, pk=courier_id)
            order.courier = courier
            order.status = 'in_progress'
            order.save()

            courier.status = 'delivering'
            courier.current_order = order
            courier.save()

            messages.success(request, f'Курьер {courier.full_name} назначен на заказ #{order.number}')
        else:
            messages.error(request, 'Не выбран курьер')

    return redirect('order_detail', order_id=order_id)


class OrderCreateView(CreateView):
    """Создание заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'main/order_form.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Автоматический расчет стоимости доставки
        response = super().form_valid(form)
        self.object.calculate_delivery_cost()
        self.object.save()
        return response


class OrderUpdateView(UpdateView):
    """Редактирование заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'main/order_form.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Пересчет доставки при изменении суммы
        if 'order_amount' in form.changed_data:
            form.instance.calculate_delivery_cost()
        return super().form_valid(form)


def change_status(request, order_id):
    """Изменение статуса заказа"""
    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get('status')

    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()

        # Обновляем статус курьера при необходимости
        if order.courier:
            if new_status == 'delivered':
                order.courier.status = 'available'
                order.courier.current_order = None
                order.courier.save()

        messages.success(request, f'Статус заказа #{order.number} изменен на "{order.get_status_display()}"')

    return redirect('order_detail', order_id=order.id)


def cancel_order(request, order_id: int):
    """Отмена заказа"""
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        # Проверяем, можно ли отменить заказ (например, только новые или в процессе)
        if order.status in ['new', 'in_progress']:
            order.status = 'canceled'

            # Если был назначен курьер - освобождаем его
            if order.courier:
                order.courier.status = 'available'
                order.courier.current_order = None
                order.courier.save()

            order.save()
            messages.success(request, f'Заказ #{order.number} успешно отменен')
        else:
            messages.error(request, 'Невозможно отменить заказ в текущем статусе')

    return redirect('order_detail', order_id=order.id)
