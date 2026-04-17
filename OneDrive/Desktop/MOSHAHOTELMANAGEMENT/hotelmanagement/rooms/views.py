from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Room
from .forms import RoomForm
from .chatbot_logic import get_chatbot_response


def room_list(request):
    rooms = Room.objects.all()
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(room_status='occupied').count()
    return render(request, 'rooms/room_list.html', {
        'rooms': rooms,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
    })


def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form})


def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form})


def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('room_list')
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})


@csrf_exempt
def chatbot_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed.'}, status=405)
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'reply': 'Please type a message.'})
        reply = get_chatbot_response(user_message)
        return JsonResponse({'reply': reply})
    except json.JSONDecodeError:
        return JsonResponse({'reply': 'Could not read your message. Try again.'}, status=400)
    except Exception as e:
        return JsonResponse({'reply': f'Server error: {str(e)}'}, status=500)