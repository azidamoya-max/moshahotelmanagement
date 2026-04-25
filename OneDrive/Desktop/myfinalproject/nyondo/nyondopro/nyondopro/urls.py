"""
URL configuration for nyondopro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from nyondoapp import views

app_name = 'nyondoapp'

urlpatterns = [

    path('admin/', admin.site.urls),

    # ─── Authentication urls ───────────────────────────────────────────
    # Login url — default landing page
    path('', views.Login, name='login'),
    # Login url — explicit
    path('login/', views.Login, name='login'),
    # Signup url — register a new user
    path('signup/', views.signup, name='signup'),
    # Logout url
    path('logout/', views.log_out, name='logout'),

    # ─── Car section — car attendant urls ─────────────────────────────
    # Url for car attendant to register a new car at entry
    path('addcar/', views.addcar, name='addcar'),
    # Url for car attendant to see all car entries
    path('allcars/', views.car_landing, name='car_landing'),
    path('car-revenues/', views.car_revenues, name='car_revenues'),
    # Url to view details of a single car entry
    path('allcars/<int:Car_id>/', views.cardetail, name='cardetail'),
    # Url for car attendant to sign out a car
    path('allcars/<str:pk>/edit/', views.princapproval, name='princapproval'),
    # Url for entry slip after car registration
    path('allcars/<int:Car_id>/receipt/', views.car_receipt, name='car_receipt'),
    # Url for full payment receipt after sign-out
    path('allcars/<int:Car_id>/signout-receipt/', views.signout_receipt, name='signout_receipt'),

    # ─── Battery section — battery attendant urls ──────────────────────
    # Url for battery attendant to record a battery transaction
    path('addbattery/', views.addbattery, name='battery'),
    # Url for battery attendant to see all battery entries
    path('dashboard2/', views.principal_approval, name='principal_approval'),
    # Url to view details of a single battery entry
    path('dashboard2/<int:Battery_id>/', views.qtdetail, name='qtdetail'),
    # Url for battery list (alternative view)
    path('allbattery/', views.allbattery, name='allbattery'),

    # ─── Tyre section — tyre attendant urls ───────────────────────────
    # Url for tyre attendant to record a tyre transaction
    path('addtyre/', views.addtyre, name='addtyre'),
    # Url for tyre attendant to see all tyre entries
    path('dashboard3/', views.alltyre, name='procurement_approval'),
    # Url to view details of a single tyre entry
    path('dashboard3/<int:Tyre_id>/', views.qtdetailt, name='qtdetailt'),
    # Url for tyre list (alternative view)
    path('alltyre/', views.alltyre, name='alltyre'),
    path('tyre-sales/', views.tyre_sales, name='tyre_sales'),
    path('battery-sales/', views.battery_sales, name='battery_sales'),

    # ─── Director / Admin urls ─────────────────────────────────────────
    # Url for director dashboard
    path('director/', views.director_approval, name='director_approval'),
    # Url for financial reports
    path('reports/', views.reports, name='reports'),
    # ─── Manager-specific views ────────────────────────────────────────────
    path('manager-battery/', views.manager_battery, name='manager_battery'),
    path('manager-tyre/', views.manager_tyre, name='manager_tyre'),
 
    # ─── Delete URLs ───────────────────────────────────────────────────────
    path('allcars/<int:Car_id>/delete/', views.car_delete, name='car_delete'),
    path('dashboard2/<int:Battery_id>/delete/', views.battery_delete, name='battery_delete'),
    path('dashboard3/<int:Tyre_id>/delete/', views.tyre_delete, name='tyre_delete'),
 
    # ─── Edit URLs ─────────────────────────────────────────────────────────
    path('dashboard2/<int:Battery_id>/edit/', views.battery_edit, name='battery_edit'),
    path('dashboard3/<int:Tyre_id>/edit/', views.tyre_edit, name='tyre_edit'),
    
    # Url for calendar / records view
    path('calendar/', views.calendar_records, name='calendar_records'),
    # Url for mega dashboard
    path('dashboardmega/', views.requi2, name='requi2'),
    # Url for dashboard1
    path('dashboard1/', views.requi, name='requi'),

    # ─── Role landing pages ────────────────────────────────────────────
    # Legacy car landing page url (kept for backwards compatibility)
    path('car_landing/', views.car_landing, name='car_landing_old'),

    # ─── Deactivated urls (kept for reference) ────────────────────────
    #url for principle to see all requisitions
    #path('dashboard2/', views.principal_approval, name='principal_approval'),
    #url for procurement to view all requisitions
    #path('dashboard3/', views.alltyre, name='procurement_approval'),
    #url that takes accountant to the list of requisitions
    #path('dashboard4/', views.accountant_approval, name='accountant_approval'),

]