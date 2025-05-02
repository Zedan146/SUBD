from django import forms
from .models import Order, Client

class OrderForm(forms.ModelForm):
    # Поле для поиска клиента с автодополнением
    client_search = forms.CharField(
        label='Поиск клиента',
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    class Meta:
        model = Order
        fields = ['delivery_address', 'order_amount', 'client']
        widgets = {
            'client': forms.HiddenInput(),  # Скрытое поле для ID клиента
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['client_search'].initial = self.instance.client.full_name