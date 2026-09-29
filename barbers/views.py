from django.shortcuts import render,redirect,get_object_or_404
from .models import Barber
from django.http import HttpResponse
from .forms import BarberForm
# Create your views here.

def welcome_barber(request):
    return HttpResponse('<h1>Hello, Registration successfull</h1>')

def barber_info(request):
    if request.method=="POST":
        form=BarberForm(request.POST)
        print("This is form: ",form)
        if form.is_valid():
            form.save()
            return redirect('/barbers/barber_info')
    else:
        form=BarberForm()
    return render(request,'barberlink/barber_reg.html',{'form':form})