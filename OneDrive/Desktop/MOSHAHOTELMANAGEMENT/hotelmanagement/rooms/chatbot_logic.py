"""
Mosha Hotel Management System — Chatbot Logic
===============================================
Rule-based chatbot using EXACT model fields from your project.
"""

from datetime import date
from rooms.models import Room
from guests.models import Guest
from payments.models import Payment


def get_chatbot_response(message: str) -> str:
    msg = message.lower().strip()

    if any(word in msg for word in ['help', 'hello', 'hi', 'what can you do', 'commands']):
        return handle_help()

    if any(word in msg for word in ['vacant', 'available', 'free', 'not occupied', 'empty']):
        return handle_vacant_rooms()

    if any(word in msg for word in ['occupied', 'taken', 'booked', 'full']):
        return handle_occupied_rooms()

    if any(word in msg for word in ['all rooms', 'room list', 'list rooms', 'show rooms', 'rooms']):
        return handle_all_rooms()

    if 'room' in msg and any(char.isdigit() for char in msg):
        return handle_specific_room(msg)

    if any(word in msg for word in ['standard', 'deluxe', 'suite', 'executive', 'presidential']):
        return handle_rooms_by_category(msg)

    if any(word in msg for word in ['all guests', 'guest list', 'list guests', 'show guests', 'how many guests']):
        return handle_all_guests()

    if any(word in msg for word in ['guest', 'find', 'search']):
        return handle_guest_search(msg)

    if any(word in msg for word in ['revenue today', "today's revenue", 'income today']):
        return handle_revenue_today()

    if any(word in msg for word in ['total revenue', 'all revenue', 'total income']):
        return handle_revenue_total()

    if any(word in msg for word in ['mobile money', 'mobile payment', 'momo']):
        return handle_payments_by_type('mobile_money')

    if 'cash' in msg and 'payment' in msg:
        return handle_payments_by_type('cash')

    if any(word in msg for word in ['recent payments', 'latest payments', 'last payments']):
        return handle_recent_payments()

    if any(word in msg for word in ['payment', 'bill', 'paid', 'balance']):
        return handle_payment_search(msg)

    return (
        "❓ I didn't understand that. Try asking:\n\n"
        "  🛏️  'vacant rooms'\n"
        "  🛏️  'room 101'\n"
        "  👤  'guest Nakato'\n"
        "  💰  'revenue today'\n"
        "  💰  'payment for Mukasa'\n\n"
        "Type 'help' for the full list."
    )


def handle_help() -> str:
    return (
        "👋 Welcome to Mosha HMS Assistant!\n\n"
        "🛏️  ROOMS\n"
        "  • 'vacant rooms'\n"
        "  • 'occupied rooms'\n"
        "  • 'all rooms'\n"
        "  • 'room 101'\n"
        "  • 'deluxe rooms'\n\n"
        "👤  GUESTS\n"
        "  • 'guest Nakato'\n"
        "  • 'all guests'\n\n"
        "💰  PAYMENTS\n"
        "  • 'revenue today'\n"
        "  • 'total revenue'\n"
        "  • 'payment for Mukasa'\n"
        "  • 'mobile money payments'\n"
        "  • 'recent payments'\n"
    )


def handle_vacant_rooms() -> str:
    rooms = Room.objects.filter(room_status='not_occupied').order_by('room_number')
    if not rooms.exists():
        return "🚫 No vacant rooms right now. All rooms are occupied."
    lines = [f"✅ {rooms.count()} vacant room(s):\n"]
    for r in rooms:
        lines.append(f"  • Room {r.room_number} — {r.get_room_category_display()}")
    return "\n".join(lines)


def handle_occupied_rooms() -> str:
    rooms = Room.objects.filter(room_status='occupied').order_by('room_number')
    if not rooms.exists():
        return "✅ No rooms are currently occupied."
    lines = [f"🔴 {rooms.count()} occupied room(s):\n"]
    for r in rooms:
        lines.append(f"  • Room {r.room_number} — {r.get_room_category_display()}")
    return "\n".join(lines)


def handle_all_rooms() -> str:
    rooms = Room.objects.all().order_by('room_number')
    if not rooms.exists():
        return "No rooms found in the system."
    vacant = rooms.filter(room_status='not_occupied').count()
    occupied = rooms.filter(room_status='occupied').count()
    lines = [f"🏨 All rooms ({rooms.count()} total | ✅ {vacant} vacant | 🔴 {occupied} occupied):\n"]
    for r in rooms:
        status = "✅ Vacant" if r.room_status == 'not_occupied' else "🔴 Occupied"
        lines.append(f"  • Room {r.room_number} — {r.get_room_category_display()} — {status}")
    return "\n".join(lines)


def handle_specific_room(msg: str) -> str:
    import re
    numbers = re.findall(r'\d+', msg)
    if not numbers:
        return "Please include a room number, e.g. 'room 101'."
    try:
        room = Room.objects.get(room_number=numbers[0])
        status = "✅ Vacant" if room.room_status == 'not_occupied' else "🔴 Occupied"
        reply = (
            f"🛏️  Room {room.room_number}\n"
            f"   Category: {room.get_room_category_display()}\n"
            f"   Status:   {status}"
        )
        if room.room_status == 'occupied':
            recent = Payment.objects.filter(room=room).order_by('-payment_date').first()
            if recent:
                reply += f"\n   Last Payment: {recent.guest.first_name} {recent.guest.last_name} — UGX {recent.amount:,.0f} ({recent.payment_date})"
        return reply
    except Room.DoesNotExist:
        return f"❌ Room {numbers[0]} does not exist in the system."


def handle_rooms_by_category(msg: str) -> str:
    category_map = {
        'standard': 'standard',
        'deluxe': 'deluxe',
        'suite': 'suite',
        'executive': 'executive',
        'presidential': 'presidential',
    }
    matched_key = next((v for k, v in category_map.items() if k in msg), None)
    if not matched_key:
        return "Please specify a category: standard, deluxe, suite, executive, or presidential."
    rooms = Room.objects.filter(room_category=matched_key).order_by('room_number')
    if not rooms.exists():
        return f"No {matched_key} rooms found."
    lines = [f"🏨 {rooms.count()} {matched_key.title()} room(s):\n"]
    for r in rooms:
        status = "✅ Vacant" if r.room_status == 'not_occupied' else "🔴 Occupied"
        lines.append(f"  • Room {r.room_number} — {status}")
    return "\n".join(lines)


def handle_all_guests() -> str:
    guests = Guest.objects.all().order_by('last_name')
    if not guests.exists():
        return "No guests found in the system."
    lines = [f"👥 {guests.count()} guest(s) registered:\n"]
    for g in guests:
        lines.append(
            f"  • {g.first_name} {g.last_name}\n"
            f"    📞 {g.phone_number} | ✉️  {g.email_address}\n"
            f"    📅 Registered: {g.date_registered}"
        )
    return "\n".join(lines)


def handle_guest_search(msg: str) -> str:
    stopwords = ['guest', 'find', 'search', 'for', 'look', 'up', 'show', 'me', 'get']
    words = msg.split()
    name_parts = [w for w in words if w not in stopwords and not w.isdigit()]
    if not name_parts:
        return "Please include a name, e.g. 'guest Nakato' or 'find Mukasa'."
    search_name = " ".join(name_parts)
    guests = (
        Guest.objects.filter(first_name__icontains=search_name) |
        Guest.objects.filter(last_name__icontains=search_name)
    )
    if not guests.exists():
        return f"❌ No guest found matching '{search_name}'."
    lines = [f"👤 Found {guests.count()} guest(s) matching '{search_name}':\n"]
    for g in guests:
        payments = Payment.objects.filter(guest=g)
        total_paid = sum(p.amount for p in payments)
        lines.append(
            f"  • {g.first_name} {g.last_name}\n"
            f"    📞 {g.phone_number}\n"
            f"    ✉️  {g.email_address}\n"
            f"    📅 Registered: {g.date_registered}\n"
            f"    💰 Total paid: UGX {total_paid:,.0f} ({payments.count()} payment(s))"
        )
    return "\n".join(lines)


def handle_revenue_today() -> str:
    today = date.today()
    payments = Payment.objects.filter(payment_date=today)
    if not payments.exists():
        return f"💰 No payments recorded today ({today}) yet."
    total = sum(p.amount for p in payments)
    mobile = sum(p.amount for p in payments if p.payment_type == 'mobile_money')
    cash = sum(p.amount for p in payments if p.payment_type == 'cash')
    return (
        f"💰 Revenue for {today}:\n"
        f"   Total:        UGX {total:,.0f}\n"
        f"   Mobile Money: UGX {mobile:,.0f}\n"
        f"   Cash:         UGX {cash:,.0f}\n"
        f"   Transactions: {payments.count()}"
    )


def handle_revenue_total() -> str:
    payments = Payment.objects.all()
    if not payments.exists():
        return "No payment records found in the system."
    total = sum(p.amount for p in payments)
    mobile = sum(p.amount for p in payments if p.payment_type == 'mobile_money')
    cash = sum(p.amount for p in payments if p.payment_type == 'cash')
    return (
        f"💰 All-time revenue:\n"
        f"   Total:        UGX {total:,.0f}\n"
        f"   Mobile Money: UGX {mobile:,.0f}\n"
        f"   Cash:         UGX {cash:,.0f}\n"
        f"   Transactions: {payments.count()}"
    )


def handle_payments_by_type(payment_type: str) -> str:
    payments = Payment.objects.filter(
        payment_type=payment_type
    ).select_related('guest', 'room').order_by('-payment_date')[:10]
    label = "Mobile Money" if payment_type == 'mobile_money' else "Cash"
    if not payments.exists():
        return f"No {label} payments found."
    total = sum(p.amount for p in payments)
    lines = [f"💳 Recent {label} payments (last 10) | Total: UGX {total:,.0f}\n"]
    for p in payments:
        lines.append(
            f"  • {p.guest.first_name} {p.guest.last_name} "
            f"— Room {p.room.room_number} "
            f"— UGX {p.amount:,.0f} "
            f"— {p.payment_date}"
        )
    return "\n".join(lines)


def handle_recent_payments() -> str:
    payments = Payment.objects.all().select_related('guest', 'room').order_by('-payment_date')[:10]
    if not payments.exists():
        return "No payments recorded yet."
    lines = ["💳 Latest 10 payments:\n"]
    for p in payments:
        type_label = "📱 Mobile" if p.payment_type == 'mobile_money' else "💵 Cash"
        lines.append(
            f"  • {p.guest.first_name} {p.guest.last_name} "
            f"— Room {p.room.room_number} "
            f"— UGX {p.amount:,.0f} "
            f"— {type_label} "
            f"— {p.payment_date}"
        )
    return "\n".join(lines)


def handle_payment_search(msg: str) -> str:
    stopwords = ['payment', 'bill', 'balance', 'paid', 'for', 'of', 'show', 'me', 'find', 'get']
    words = msg.split()
    name_parts = [w for w in words if w not in stopwords and not w.isdigit()]
    if not name_parts:
        return "Please include a guest name, e.g. 'payment for Mukasa'."
    search_name = " ".join(name_parts)
    guests = (
        Guest.objects.filter(first_name__icontains=search_name) |
        Guest.objects.filter(last_name__icontains=search_name)
    )
    if not guests.exists():
        return f"❌ No guest found matching '{search_name}'."
    lines = []
    for g in guests:
        payments = Payment.objects.filter(guest=g).order_by('-payment_date')
        if not payments.exists():
            lines.append(f"• {g.first_name} {g.last_name} — No payments on record.")
            continue
        total = sum(p.amount for p in payments)
        lines.append(f"💳 {g.first_name} {g.last_name} — {payments.count()} payment(s) | Total: UGX {total:,.0f}\n")
        for p in payments:
            type_label = "📱 Mobile Money" if p.payment_type == 'mobile_money' else "💵 Cash"
            lines.append(
                f"    • Room {p.room.room_number} "
                f"— UGX {p.amount:,.0f} "
                f"— {type_label} "
                f"— {p.payment_date}"
            )
    return "\n".join(lines)