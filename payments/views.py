from django.shortcuts import render, redirect
from .models import Payment
from .serializers import PaymentSerializer
from barbers.models import Barber


def payment_success(request):
    return render(request, 'barberlink/payment_success.html')


def payment_failed(request):
    return render(request, 'barberlink/payment_fail.html')


def save_payment(request):

    payment_id = request.GET.get("payment_id")
    status = request.GET.get("status")
    barber_id = request.GET.get("barber_id")

    barber = Barber.objects.get(barber_id=barber_id)

    payment = Payment.objects.create(
        barber_id=barber,
        amount=120,
        payment_status=status,
        razorpay_transaction_id=payment_id
    )

    payment_data = PaymentSerializer(payment).data

    print(payment_data)

    if status == "success":
        return redirect("payment_success_dashboard")

    return redirect("payment_failed_dashboard")