from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from .models import Table, Customer, Confirmation
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.contrib import messages
import pytz
from django.urls import reverse
import logging
from time import sleep
from random import uniform
import logging
logger = logging.getLogger(__name__)

def table(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())

def menu(request):
    template = loader.get_template('menu.html')
    return HttpResponse(template.render())

@transaction.atomic
def book_table(request):
    if request.method == "POST":
        tablename = request.POST.get('table', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phoneNr = request.POST.get('phone', '').strip()
        bookingdate = request.POST.get('bookingdate', '').strip()
        bookingstart = request.POST.get('bookingstart', '').strip()
        bookingend = request.POST.get('bookingend', '').strip()

        retries = 3
        for attempt in range(retries):
            try:
                with transaction.atomic():
                    local_tz = pytz.timezone('Europe/Stockholm')
                    booking_date = datetime.strptime(bookingdate, '%Y-%m-%d').date()
                    booking_start_time = datetime.strptime(bookingstart, '%H:%M').time()
                    booking_end_time = datetime.strptime(bookingend, '%H:%M').time()

                    booking_start_datetime = timezone.make_aware(datetime.combine(booking_date, booking_start_time), local_tz)
                    booking_end_datetime = timezone.make_aware(datetime.combine(booking_date, booking_end_time), local_tz)

                    table_shape, table_id = tablename.split()[0], int(tablename.split()[-1])
                    table = Table.objects.select_for_update().get(shape=table_shape, tableID=table_id)

                    if table.is_occupied:
                        return redirect(f"{reverse('error')}?error_message=This table is already booked.")

                    customer = Customer(name=name, email=email, phoneNr=phoneNr)
                    customer.full_clean()
                    customer.save()

                    table.is_occupied = True
                    table.save()

                    confirmation = Confirmation(
                        tableID=table,
                        customerID=customer,
                        status=True,
                        booking_date=booking_date,
                        booking_start=booking_start_time,
                        booking_end=booking_end_time
                    )
                    confirmation.save()

                    # Check if more than one booking exists for the same table and time
                    overlapping_bookings = Confirmation.objects.filter(
                        tableID=table,
                        booking_date=booking_date,
                        booking_start__lt=booking_end_time,
                        booking_end__gt=booking_start_time
                    ).count()

                    if overlapping_bookings > 1:
                        print(f"Warning: {overlapping_bookings} bookings detected for table {table.tableID} at the same time!")

                    return HttpResponseRedirect(f"/hv/menu/booking/confirmation/?table={tablename}&name={name}&email={email}&phone={phoneNr}&seats={table.seats}&bookingdate={bookingdate}&bookingstart={bookingstart}&bookingend={bookingend}")

            except ValidationError as e:
                return redirect(f"{reverse('error')}?error_message={str(e)}")
            except IntegrityError:
                if attempt == retries - 1:
                    return redirect(f"{reverse('error')}?error_message=This table is already booked.")
                sleep(uniform(0.1, 0.3))  # Random delay before retrying
            except Exception as e:
                print(f"Unexpected error: {e}")
                return redirect(f"{reverse('error')}?error_message=An unexpected error occurred.")

    else:
        return render(request, 'book.html', {'tables': Table.objects.all()})
def delete_past_bookings_view(request):
    if request.method == "POST":
        print("TRYING TO DELETE")
        delete_past_bookings()
        messages.success(request, "Förflutna bokningar har tagits bort.")
        return redirect('tables')
    else:
        return HttpResponse("Ogiltig förfrågan.", status=405)



def delete_past_bookings():
    # Define the time zone (e.g., 'Europe/Stockholm')
    local_tz = pytz.timezone('Europe/Stockholm')

    # Get the current time in the specified time zone
    now_local = timezone.localtime(timezone=local_tz)

    print(f"Current time in Stockholm: {now_local}")


    past_bookings = Confirmation.objects.filter(
        booking_date__lt=now_local.date()
    ) | Confirmation.objects.filter(
        booking_date=now_local.date(), booking_end__lt=now_local.time()  # Bookings from today but have ended
    )

    print(f"Found {past_bookings.count()} past bookings to delete.")

    # Delete past bookings and reset table status
    for booking in past_bookings:
        print(f"Deleting booking: {booking.confirmID}, Table: {booking.tableID.tableID}, Date: {booking.booking_date}, End Time: {booking.booking_end}")
        table = booking.tableID
        table.is_occupied = False
        table.save()
        print(f"Reset table {table.tableID} to available.")
    customer_ids = set(past_bookings.values_list('customerID__customerID', flat=True))

    past_bookings.delete()
    for customer_id in customer_ids:
        if not Confirmation.objects.filter(customerID__customerID=customer_id).exists():
            Customer.objects.filter(customerID=customer_id).delete()
            print(f"Deleted customer with ID: {customer_id}")
        else:
            print(f"Customer {customer_id} still has active bookings.")

    print("Deleted past bookings and reset table status")
def error_view(request):
    error_message = request.GET.get('error_message', 'An unspecified error occurred.')
    return render(request, 'error.html', {'error_message': error_message})
def confirm(request):
    table = request.GET.get('table', '').strip("[]'")
    name = request.GET.get('name', '').strip("[]'")
    email = request.GET.get('email', '').strip("[]'")
    phone = request.GET.get('phone', '').strip("[]'")
    bookingdate = request.GET.get('bookingdate', '').strip("[]'")
    bookingstart = request.GET.get('bookingstart', '').strip("[]'")
    bookingend = request.GET.get('bookingend', '').strip("[]'")

    context = {
        'table': table,
        'name': name,
        'email': email,
        'phone': phone,
        'bookingdate': bookingdate,
        'bookingstart': bookingstart,
        'bookingend': bookingend,
    }

    return render(request, 'confirmation.html', context)

def contact(request):
    template = loader.get_template('contact.html')
    return HttpResponse(template.render())