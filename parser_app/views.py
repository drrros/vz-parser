from django.shortcuts import render

from .models import Contract, Order, Update


def home(request):
    context = {
        'contracts': Contract.objects.filter(contract_date__gt='2019-12-20').order_by('-contract_date', 'id'),
        'orders': Order.objects.order_by('-order_date', 'id')[:15],
        'last_updated': Update.objects.get(id=1)
    }
    return render(request, 'index.html', context=context)
