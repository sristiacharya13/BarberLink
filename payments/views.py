from django.shortcuts import render, redirect
from .models import Payment
from .serializers import PaymentSerializer
from barbers.models import Barber
import razorpay
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

def record_successful_payment(barber, amount, transaction_id):
    Payment.objects.create(
        barber_id=barber,
        amount=amount,
        payment_status="success",
        razorpay_transaction_id=transaction_id,
    )
    barber.subscription_status = Barber.STATUS_ACTIVE
    today = timezone.localdate()
    try:
        barber.subscription_expiry_date = today.replace(year=today.year + 1)
    except ValueError:
        barber.subscription_expiry_date = today + timedelta(days=365)
    barber.save(update_fields=["subscription_status", "subscription_expiry_date"])

def payment_success(request):
    return render(request, 'barberlink/payment_success.html')


def payment_failed(request):
    return render(request, 'barberlink/payment_fail.html')

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_payment(request):
    if request.user.role!="barber":
        return Response({"error":{"code":"FORBIDDEN"}},status=403)
    barber=request.user.barber

    # payment_id = request.GET.get("payment_id")
    # status = request.GET.get("status")
    # barber_id = request.GET.get("barber_id")
    payment_id = request.data.get("razorpay_payment_id")
    order_id = request.data.get("razorpay_order_id")
    signature = request.data.get("razorpay_signature")

    client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

    # payment = Payment.objects.create(
    #     barber_id=barber,
    #     amount=120,
    #     payment_status=status,
    #     razorpay_transaction_id=payment_id
    # )

    # payment_data = PaymentSerializer(payment).data

    # print(payment_data)

    # if status == "success":
    #     return redirect("payment_success_dashboard")

    # return redirect("payment_failed_dashboard")\
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id":order_id,
            "razorpay_payment_id":payment_id,
            "razorpay_signature":signature,
        })
    except razorpay.errors.SignatureVerficationError:
        return Response({
            "error":{"code":"INVALID_SIGNATURE"}
        },status=400)

    if Payment.objects.filter(razorpay_transaction_id=payment_id).exists():
        return Response({"status":"already_recorded"})

    record_successful_payment(barber,499,payment_id)
    return Response({"status":"success","expiry":barber.subscription_expiry_date})