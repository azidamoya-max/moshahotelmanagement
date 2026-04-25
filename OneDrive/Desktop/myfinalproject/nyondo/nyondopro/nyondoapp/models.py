from django.db import models
from django.contrib.auth.models import AbstractUser

# ─── Supporting models ─────────────────────────────────────────────────────────

class Price(models.Model):
    bprice = models.CharField(max_length=200)
    def __str__(self):
        return self.bprice

class Tprice(models.Model):
    tprice = models.CharField(max_length=200)
    def __str__(self):
        return self.tprice

class Batterybrand(models.Model):
    batterybrand = models.CharField(max_length=200)
    def __str__(self):
        return self.batterybrand

class Tyrebrand(models.Model):
    tyrebrand = models.CharField(max_length=200)
    def __str__(self):
        return self.tyrebrand

# ─── User profile ──────────────────────────────────────────────────────────────

class Userprofile(AbstractUser):
    is_director = models.BooleanField(default=True)
    is_battery = models.BooleanField(default=True)
    is_tyre = models.BooleanField(default=True)
    is_car = models.BooleanField(default=True)
    username = models.CharField(max_length=50, unique=True)
    department = models.CharField(choices=[
        ('Administration', 'Administration'),
        ('Battery', 'Battery'),
        ('Tyre', 'Tyre'),
        ('Records', 'Records')],
        max_length=50,
        unique=True,
        default=True
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# ─── Parking slot model ────────────────────────────────────────────────────────

class ParkingSlot(models.Model):
    number = models.IntegerField(unique=True, verbose_name='Slot Number')
    status = models.CharField(
        choices=[('FREE', 'Free'), ('OCCUPIED', 'Occupied')],
        max_length=10,
        default='FREE',
        verbose_name='Slot Status'
    )

    def __str__(self):
        return f'Slot {self.number}'

    class Meta:
        ordering = ['number']

# ─── Car model ─────────────────────────────────────────────────────────────────

class Car(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    sign_out_time = models.DateTimeField(null=True, blank=True)
    car_brand = models.CharField(max_length=100, verbose_name='Car Brand', null=True, blank=True)
    cparktype = models.CharField(choices=[
        ('TRUCK', 'Truck'),
        ('PERSONAL CAR', 'Personal Car'),
        ('TAXI', 'Taxi'),
        ('COASTER', 'Coaster'),
        ('BODA-BODA', 'Boda-boda')],
        max_length=30,
        default='PERSONAL CAR',
        null=True,
        blank=True,
        verbose_name='Vehicle Type'
    )
    customer = models.CharField(verbose_name='Driver First Name', max_length=255, null=True, blank=True)
    customerv = models.CharField(verbose_name='Driver Other Name', max_length=255, null=True, blank=True)
    customerNiN = models.CharField(verbose_name='Customer NIN', max_length=255, null=True, blank=True)
    phone = models.CharField(verbose_name='Phone Number', max_length=20, null=True, blank=True)
    cnumberplate = models.CharField(verbose_name='Car Number Plate', max_length=255, null=True, blank=True)
    color = models.CharField(verbose_name='Color of the Car', max_length=255, null=True, blank=True)
    fee = models.IntegerField(verbose_name='Parking Fee (UGX)', null=True, blank=True)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Parking Slot')
    p_status = models.CharField(choices=[
        ('PARKED', 'Parked'),
        ('COLLECTED', 'Collected'),
        ('OVERDUE', 'Overdue')],
        max_length=10,
        verbose_name='Car Status',
        default='PARKED',
        null=True,
        blank=True,
    )
    cparkv = models.CharField(choices=[
        ('NO', 'NO'),
        ('YES', 'YES')],
        max_length=30,
        default='NO',
        null=True,
        blank=True,
        verbose_name='Have you verified?'
    )
    cparkpaymode = models.CharField(choices=[
        ('CASH', 'CASH'),
        ('MM', 'MM')],
        max_length=30,
        default='CASH',
        null=True,
        blank=True,
        verbose_name='Parking Payment Mode'
    )

    def __str__(self):
        return self.cnumberplate or 'No Plate'

# ─── Battery model ─────────────────────────────────────────────────────────────

class Battery(models.Model):
    batery_brand = models.ForeignKey(Batterybrand, on_delete=models.CASCADE, verbose_name='Battery brand')
    price = models.ForeignKey(Price, on_delete=models.CASCADE, verbose_name='Battery price')
    qty = models.CharField(verbose_name='Item Quantity', max_length=255, null=True, blank=True)
    customer = models.CharField(verbose_name='Customer Name', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    transaction_type = models.CharField(
        choices=[('SOLD', 'Sold'), ('HIRED', 'Hired')],
        max_length=10,
        default='SOLD',
        verbose_name='Transaction Type'
    )
    decription = models.CharField(verbose_name='Any other details', null=True, blank=True, max_length=250)
    voltage = models.CharField(verbose_name='Battery Voltage (e.g. 12V)', max_length=255)
    bmodel = models.CharField(verbose_name='Battery Model (e.g. nz70)', max_length=255)
    payment_mode = models.CharField(
        choices=[('CASH', 'Cash'), ('MM', 'Mobile Money')],
        max_length=20,
        default='CASH',
        verbose_name='Payment Mode'
    )

    def __str__(self):
        return self.voltage or 'No voltage'

# ─── Tyre model ────────────────────────────────────────────────────────────────

class Tyre(models.Model):
    tyre_brand = models.ForeignKey(Tyrebrand, on_delete=models.CASCADE, verbose_name='Tyre brand')
    price = models.ForeignKey(Tprice, on_delete=models.CASCADE, verbose_name='Tyre price')
    qty = models.CharField(verbose_name='Item Quantity', max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    decription = models.CharField(verbose_name='Any other details', null=True, blank=True, max_length=250)
    size = models.CharField(verbose_name='Tyre size', max_length=255, null=False, blank=False)
    customer = models.CharField(verbose_name='Customer Name', max_length=255, null=True, blank=True)
    serial = models.CharField(verbose_name='Serial number', max_length=255, null=True, blank=True)
    payment_mode = models.CharField(
        choices=[('CASH', 'Cash'), ('MM', 'Mobile Money')],
        max_length=20,
        default='CASH',
        verbose_name='Payment Mode'
    )

    def __str__(self):
        return self.size