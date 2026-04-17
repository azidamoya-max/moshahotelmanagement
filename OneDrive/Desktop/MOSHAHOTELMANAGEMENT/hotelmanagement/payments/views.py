from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment
from .forms import PaymentForm
from guests.models import Guest
from rooms.models import Room

def payment_list(request):
    payments = Payment.objects.all()
    total_revenue = sum(p.amount for p in payments)
    return render(request, 'payments/payment_list.html', {
        'payments': payments,
        'total_revenue': total_revenue,
    })

def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment_list')
    else:
        form = PaymentForm()
    guests = Guest.objects.all()
    rooms = Room.objects.all()
    payments = Payment.objects.all()
    return render(request, 'payments/payment_form.html', {
        'form': form,
        'guests': guests,
        'rooms': rooms,
        'payments': payments,
    })

def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return redirect('payment_list')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})