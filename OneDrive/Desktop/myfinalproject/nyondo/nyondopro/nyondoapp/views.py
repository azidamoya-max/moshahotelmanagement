from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views import generic
from .filters import TyreFilter
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
from .forms import *
from .models import *


# ─── Login view ────────────────────────────────────────────────────────────────

def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_director:
                return redirect('/director')
            elif user.is_battery:
                return redirect('/dashboard2')
            elif user.is_tyre:
                return redirect('/dashboard3')
            elif user.is_car:
                return redirect('/allcars/')
            else:
                messages.info(request, 'Account has no role assigned!')
        else:
            messages.info(request, 'Account does not exist, please sign in!')
    form = AuthenticationForm()
    return render(request, 'nyondoapp/login.html', {'form': form, 'title': 'login'})


# ─── Login redirect view ───────────────────────────────────────────────────────

def login_view(request):
    return render(request, 'nyondoapp/login.html')


# ─── Signup view ───────────────────────────────────────────────────────────────

def signup(request):
    if request.method == "POST":
        form = UserCreation(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = UserCreation()
    return render(request, 'nyondoapp/signup.html', {'form': form})


# ─── Logout view ───────────────────────────────────────────────────────────────

@login_required
def log_out(request):
    logout(request)
    return redirect('/login')


# ─── General requisition views ─────────────────────────────────────────────────

def requi(request):
    form = RequiForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Record saved successfully!')
        else:
            print('something is wrong')
    return render(request, 'nyondoapp/requisition.html', {'form': form})


@login_required
def requi2(request):
    form = RequiForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Record saved successfully!')
        else:
            print('something is wrong')
    return render(request, 'requisit/requisitionBig.html', {'form': form})


# ─── Car section views ─────────────────────────────────────────────────────────

@login_required
def car_landing(request):
    cutoff = timezone.now() - timedelta(hours=24)
    Car.objects.filter(
        p_status='PARKED',
        created_at__lt=cutoff
    ).update(p_status='OVERDUE')

    q = request.GET.get('q', '')
    if q:
        qt = Car.objects.filter(
            car_brand__icontains=q
        ) | Car.objects.filter(
            cnumberplate__icontains=q
        ) | Car.objects.filter(
            customer__icontains=q
        )
        qt = qt.order_by('-id')
    else:
        qt = Car.objects.all().order_by('-id')

    total_slots    = ParkingSlot.objects.count()
    occupied_slots = ParkingSlot.objects.filter(status='OCCUPIED').count()
    free_slots     = total_slots - occupied_slots

    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    return render(request, 'nyondoapp/allcars.html', {
        'page_obj':       page_obj,
        'q':              q,
        'total_slots':    total_slots,
        'occupied_slots': occupied_slots,
        'free_slots':     free_slots,
    })


@login_required
def addcar(request):
    form = AddcarForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            car = form.save(commit=False)
            car.p_status = 'PARKED'
            car.save()
            if car.slot:
                car.slot.status = 'OCCUPIED'
                car.slot.save()
            messages.success(request, 'Car registered successfully!')
            return redirect(f'/allcars/{car.id}/receipt/')
        else:
            print('Form errors:', form.errors)
    free_slots = ParkingSlot.objects.filter(status='FREE').count()
    return render(request, 'nyondoapp/dashboard4.html', {
        'form':       form,
        'free_slots': free_slots,
    })


@login_required
def cardetail(request, Car_id):
    qtdetails = Car.objects.get(id=Car_id)
    return render(request, 'nyondoapp/detail3.html', {'qtdetails': qtdetails})


@login_required
def car_receipt(request, Car_id):
    car = Car.objects.get(id=Car_id)
    return render(request, 'nyondoapp/car_receipt.html', {'car': car})


# ─── Car sign-out view ─────────────────────────────────────────────────────────

@login_required
def princapproval(request, pk):
    car = Car.objects.get(id=pk)
    form = CarSignOutForm(request.POST or None, instance=car)
    if request.method == 'POST':
        if form.is_valid():
            signout = form.save(commit=False)
            signout.sign_out_time = timezone.now()
            signout.p_status = 'COLLECTED'
            signout.save()
            if car.slot:
                car.slot.status = 'FREE'
                car.slot.save()
            messages.success(request, 'Car signed out successfully!')
            return redirect(f'/allcars/{car.id}/signout-receipt/')
        else:
            print('Form errors:', form.errors)
    duration = None
    if car.created_at:
        duration = timezone.now() - car.created_at
    return render(request, 'nyondoapp/caredit.html', {
        'form':     form,
        'car':      car,
        'duration': duration,
    })


@login_required
def signout_receipt(request, Car_id):
    car = Car.objects.get(id=Car_id)
    duration = None
    if car.created_at and car.sign_out_time:
        duration = car.sign_out_time - car.created_at
    return render(request, 'nyondoapp/signout_receipt.html', {
        'car':      car,
        'duration': duration,
    })


# ─── Battery section views ─────────────────────────────────────────────────────

@login_required
def addbattery(request):
    form = AddbatteryForm(request.POST or None, request.FILES or None)
    show_receipt = False
    receipt = {}

    if request.method == 'POST':
        if form.is_valid():
            battery = form.save()
            try:
                raw_price = ''.join(filter(str.isdigit, battery.price.bprice))
                unit_price = int(raw_price)
                qty = int(battery.qty)
                total = unit_price * qty
            except (ValueError, AttributeError):
                total = 0
            show_receipt = True
            receipt = {
                'customer': battery.customer,
                'brand': battery.batery_brand,
                'voltage': battery.voltage,
                'bmodel': battery.bmodel,
                'transaction_type': battery.transaction_type,
                'qty': battery.qty,
                'payment_mode': battery.payment_mode,
                'price': f"{total:,}",
                'date': battery.created_at.strftime('%d %b %Y %H:%M') if battery.created_at else '',
            }
            messages.success(request, 'Battery transaction recorded successfully!')
        else:
            print(form.errors)

    return render(request, 'nyondoapp/addbattery.html', {
        'form': form,
        'show_receipt': show_receipt,
        'receipt': receipt,
    })


@login_required
def principal_approval(request):
    q = request.GET.get('q', '')
    if q:
        qt = Battery.objects.filter(
            voltage__icontains=q
        ) | Battery.objects.filter(
            customer__icontains=q
        ) | Battery.objects.filter(
            transaction_type__icontains=q
        )
        qt = qt.order_by('-id')
    else:
        qt = Battery.objects.all().order_by('-id')
    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'nyondoapp/allbatterybp.html', {'page_obj': page_obj, 'q': q})


@login_required
def qtdetail(request, Battery_id):
    qtdetails = Battery.objects.get(id=Battery_id)
    try:
        raw_price = ''.join(filter(str.isdigit, qtdetails.price.bprice))
        total = int(raw_price) * int(qtdetails.qty)
        total_display = f"{total:,}"
    except (ValueError, AttributeError):
        total_display = qtdetails.price.bprice if qtdetails.price else '—'
    return render(request, 'nyondoapp/detail.html', {
        'qtdetails': qtdetails,
        'total': total_display,
    })


@login_required
def allbattery(request):
    qt = Battery.objects.all().order_by('-id')
    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'nyondoapp/allbattery.html', {'page_obj': page_obj})


# ─── Tyre section views ────────────────────────────────────────────────────────

@login_required
def addtyre(request):
    form = AddtyreForm(request.POST or None)
    show_receipt = False
    receipt = {}

    if request.method == 'POST':
        if form.is_valid():
            tyre = form.save()
            try:
                raw_price = ''.join(filter(str.isdigit, tyre.price.tprice))
                unit_price = int(raw_price)
                qty = int(tyre.qty)
                total = unit_price * qty
            except (ValueError, AttributeError):
                total = 0
            show_receipt = True
            receipt = {
                'customer': tyre.customer,
                'brand': tyre.tyre_brand,
                'size': tyre.size,
                'serial': tyre.serial,
                'qty': tyre.qty,
                'payment_mode': tyre.payment_mode,
                'price': f"{total:,}",
                'date': tyre.created_at.strftime('%d %b %Y %H:%M') if tyre.created_at else '',
            }
            messages.success(request, 'Tyre transaction recorded successfully!')
        else:
            print(form.errors)

    return render(request, 'nyondoapp/addtyre.html', {
        'form': form,
        'show_receipt': show_receipt,
        'receipt': receipt,
    })


@login_required
def procurement_approval(request):
    qt = Tyre.objects.all().order_by('-id')
    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'nyondoapp/procurement.html', {'page_obj': page_obj})


@login_required
def qtdetailt(request, Tyre_id):
    qtdetails = Tyre.objects.get(id=Tyre_id)
    try:
        raw_price = ''.join(filter(str.isdigit, qtdetails.price.tprice))
        total = int(raw_price) * int(qtdetails.qty)
        total_display = f"{total:,}"
    except (ValueError, AttributeError):
        total_display = qtdetails.price.tprice if qtdetails.price else '—'
    return render(request, 'nyondoapp/detail2.html', {
        'qtdetails': qtdetails,
        'total': total_display,
    })


@login_required
def alltyre(request):
    qt = Tyre.objects.all().order_by('-id')
    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'nyondoapp/alltyre.html', {'page_obj': page_obj})


# ─── Director / Admin views ────────────────────────────────────────────────────

@login_required
def director_approval(request):
    date_from_str = request.GET.get('from', '')
    date_to_str   = request.GET.get('to', '')
    today = timezone.now()

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d') if date_from_str else today.replace(day=1)
    except ValueError:
        date_from = today.replace(day=1)

    try:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d') if date_to_str else today
    except ValueError:
        date_to = today

    selected_date_str = request.GET.get('date', '')
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else today.date()
    except ValueError:
        selected_date = today.date()

    qt          = Car.objects.all().order_by('-id')
    paginator   = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    cars_filtered = Car.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        fee__isnull=False
    )
    car_revenue = sum(c.fee for c in cars_filtered if c.fee)
    car_total   = cars_filtered.count()

    batteries_filtered = Battery.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        price__isnull=False
    )
    battery_revenue = 0
    for b in batteries_filtered:
        try:
            raw = ''.join(filter(str.isdigit, b.price.bprice))
            battery_revenue += int(raw) * int(b.qty)
        except (ValueError, AttributeError):
            pass
    battery_total = batteries_filtered.count()

    tyres_filtered = Tyre.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        price__isnull=False
    )
    tyre_revenue = 0
    for t in tyres_filtered:
        try:
            raw = ''.join(filter(str.isdigit, t.price.tprice))
            tyre_revenue += int(raw) * int(t.qty)
        except (ValueError, AttributeError):
            pass
    tyre_total = tyres_filtered.count()

    grand_total = car_revenue + battery_revenue + tyre_revenue

    cal_cars      = Car.objects.filter(created_at__date=selected_date).order_by('-created_at')
    cal_batteries = Battery.objects.filter(created_at__date=selected_date).order_by('-created_at')
    cal_tyres     = Tyre.objects.filter(created_at__date=selected_date).order_by('-created_at')

    return render(request, 'nyondoapp/director.html', {
        'page_obj':          page_obj,
        'date_from':         date_from.strftime('%Y-%m-%d'),
        'date_to':           date_to.strftime('%Y-%m-%d'),
        'grand_total':       grand_total,
        'car_revenue':       car_revenue,
        'car_total':         car_total,
        'battery_revenue':   battery_revenue,
        'battery_total':     battery_total,
        'tyre_revenue':      tyre_revenue,
        'tyre_total':        tyre_total,
        'selected_date':     selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'cal_cars':          cal_cars,
        'cal_batteries':     cal_batteries,
        'cal_tyres':         cal_tyres,
    })


# ─── Reports view ──────────────────────────────────────────────────────────────

@login_required
def reports(request):
    date_from_str = request.GET.get('from', '')
    date_to_str   = request.GET.get('to', '')
    today = timezone.now()

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d') if date_from_str else today.replace(day=1)
    except ValueError:
        date_from = today.replace(day=1)

    try:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d') if date_to_str else today
    except ValueError:
        date_to = today

    cars        = Car.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to, fee__isnull=False)
    car_revenue = sum(c.fee for c in cars if c.fee)
    car_total   = cars.count()

    batteries       = Battery.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to, price__isnull=False)
    battery_revenue = 0
    for b in batteries:
        try:
            raw = ''.join(filter(str.isdigit, b.price.bprice))
            battery_revenue += int(raw) * int(b.qty)
        except (ValueError, AttributeError):
            pass
    battery_total = batteries.count()

    tyres        = Tyre.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to, price__isnull=False)
    tyre_revenue = 0
    for t in tyres:
        try:
            raw = ''.join(filter(str.isdigit, t.price.tprice))
            tyre_revenue += int(raw) * int(t.qty)
        except (ValueError, AttributeError):
            pass
    tyre_total = tyres.count()

    grand_total = car_revenue + battery_revenue + tyre_revenue

    return render(request, 'nyondoapp/reports.html', {
        'date_from':       date_from.strftime('%Y-%m-%d'),
        'date_to':         date_to.strftime('%Y-%m-%d'),
        'car_revenue':     car_revenue,
        'car_total':       car_total,
        'battery_revenue': battery_revenue,
        'battery_total':   battery_total,
        'tyre_revenue':    tyre_revenue,
        'tyre_total':      tyre_total,
        'grand_total':     grand_total,
    })


# ─── Calendar view ─────────────────────────────────────────────────────────────

@login_required
def calendar_records(request):
    selected_date_str = request.GET.get('date', '')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    cars      = Car.objects.filter(created_at__date=selected_date).order_by('-created_at')
    batteries = Battery.objects.filter(created_at__date=selected_date).order_by('-created_at')
    tyres     = Tyre.objects.filter(created_at__date=selected_date).order_by('-created_at')

    sixty_days_ago = timezone.now().date() - timedelta(days=60)
    active_dates   = set()
    for model in [Car, Battery, Tyre]:
        dates = model.objects.filter(
            created_at__date__gte=sixty_days_ago
        ).values_list('created_at__date', flat=True)
        active_dates.update(dates)

    return render(request, 'nyondoapp/calendar_records.html', {
        'selected_date':     selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'cars':              cars,
        'batteries':         batteries,
        'tyres':             tyres,
        'active_dates':      [d.strftime('%Y-%m-%d') for d in active_dates],
    })

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Open views.py and PASTE THIS at the very bottom of the file
# ─────────────────────────────────────────────────────────────────────────────


# ─── Tyre Sales view ──────────────────────────────────────────────────────────

@login_required
def tyre_sales(request):
    tyres = Tyre.objects.all().order_by('-created_at')
    sales = []
    grand_total = 0
    for t in tyres:
        try:
            raw = ''.join(filter(str.isdigit, t.price.tprice))
            unit_price = int(raw)
            qty = int(t.qty)
            total = unit_price * qty
        except (ValueError, AttributeError):
            unit_price = 0
            qty = t.qty
            total = 0
        grand_total += total
        sales.append({
            'created_at': t.created_at,
            'tyre_brand': t.tyre_brand,
            'size': t.size,
            'qty': qty,
            'unit_price': f"{unit_price:,}",
            'total': f"{total:,}",
        })
    return render(request, 'nyondoapp/tyre_sales.html', {
        'sales': sales,
        'grand_total': f"{grand_total:,}",
        'total_count': len(sales),
    })


# ─── Battery Sales view ───────────────────────────────────────────────────────

@login_required
def battery_sales(request):
    batteries = Battery.objects.all().order_by('-created_at')
    sales = []
    grand_total = 0
    for b in batteries:
        try:
            raw = ''.join(filter(str.isdigit, b.price.bprice))
            unit_price = int(raw)
            qty = int(b.qty)
            total = unit_price * qty
        except (ValueError, AttributeError):
            unit_price = 0
            qty = b.qty
            total = 0
        grand_total += total
        sales.append({
            'created_at': b.created_at,
            'voltage': b.voltage,
            'bmodel': b.bmodel,
            'qty': qty,
            'unit_price': f"{unit_price:,}",
            'total': f"{total:,}",
        })
    return render(request, 'nyondoapp/battery_sales.html', {
        'sales': sales,
        'grand_total': f"{grand_total:,}",
        'total_count': len(sales),
    })

# ─── Car Revenues view ────────────────────────────────────────────────────────

@login_required
def car_revenues(request):
    cars = Car.objects.all().order_by('-created_at')
    revenues = []
    grand_total = 0
    for c in cars:
        try:
            fee = int(c.fee) if c.fee else 0
        except (ValueError, TypeError):
            fee = 0
        grand_total += fee
        revenues.append({
            'created_at': c.created_at,
            'car_brand': c.car_brand,
            'cnumberplate': c.cnumberplate,
            'cparktype': c.cparktype,
            'fee': f"{fee:,}",
            'p_status': c.p_status,
        })
    return render(request, 'nyondoapp/car_revenues.html', {
        'revenues': revenues,
        'grand_total': f"{grand_total:,}",
        'total_count': len(revenues),
    })

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Open views.py and PASTE THIS at the very bottom of the file
# ─────────────────────────────────────────────────────────────────────────────


# ─── Manager Battery view ─────────────────────────────────────────────────────

@login_required
def manager_battery(request):
    q = request.GET.get('q', '')
    if q:
        qt = Battery.objects.filter(
            voltage__icontains=q
        ) | Battery.objects.filter(
            bmodel__icontains=q
        ) | Battery.objects.filter(
            transaction_type__icontains=q
        )
        qt = qt.order_by('-id')
    else:
        qt = Battery.objects.all().order_by('-id')
    paginator = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'nyondoapp/manager_battery.html', {'page_obj': page_obj, 'q': q})


# ─── Manager Tyre view ────────────────────────────────────────────────────────

@login_required
def manager_tyre(request):
    q = request.GET.get('q', '')
    if q:
        qt = Tyre.objects.filter(
            size__icontains=q
        ) | Tyre.objects.filter(
            serial__icontains=q
        )
        qt = qt.order_by('-id')
    else:
        qt = Tyre.objects.all().order_by('-id')
    paginator = Paginator(qt, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'nyondoapp/manager_tyre.html', {'page_obj': page_obj, 'q': q})


# ─── Delete views ─────────────────────────────────────────────────────────────

@login_required
def car_delete(request, Car_id):
    car = get_object_or_404(Car, id=Car_id)
    car.delete()
    return redirect('/director')

@login_required
def battery_delete(request, Battery_id):
    battery = get_object_or_404(Battery, id=Battery_id)
    battery.delete()
    return redirect('/manager-battery/')

@login_required
def tyre_delete(request, Tyre_id):
    tyre = get_object_or_404(Tyre, id=Tyre_id)
    tyre.delete()
    return redirect('/manager-tyre/')


# ─── Edit views ───────────────────────────────────────────────────────────────

@login_required
def battery_edit(request, Battery_id):
    battery = get_object_or_404(Battery, id=Battery_id)
    form = AddbatteryForm(request.POST or None, request.FILES or None, instance=battery)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Battery record updated successfully!')
            return redirect('/manager-battery/')
    return render(request, 'nyondoapp/battery_edit.html', {'form': form, 'battery': battery})


@login_required
def tyre_edit(request, Tyre_id):
    tyre = get_object_or_404(Tyre, id=Tyre_id)
    form = AddtyreForm(request.POST or None, instance=tyre)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Tyre record updated successfully!')
            return redirect('/manager-tyre/')
    return render(request, 'nyondoapp/tyre_edit.html', {'form': form, 'tyre': tyre})