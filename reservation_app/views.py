import datetime

from django.shortcuts import render, redirect
from django.views import View
from .models import ConferenceRoom


class AddRoomView(View):
    def get(self, request):
        return render(request, 'reservation_app/add_room.html')

    def post(self, request):
        name = request.POST.get('room-name')
        capacity = request.POST.get('capacity')
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get('projector') == 'on'

        if not name:
            return render(
                request,
                'reservation_app/add_room.html',
                {'error': 'Nie podano nazwy sali'}
            )
        if capacity <= 0:
            return render(
                request,
                'reservation_app/add_room.html',
                {'error': 'Pojemność sali musi być dodatnia'}
            )
        if ConferenceRoom.objects.filter(name=name).first():
            return render(
                request,
                'reservation_app/add_room.html',
                {'error': 'Sala o podanej nazwie już istnieje'}
            )
        ConferenceRoom.objects.create(name=name, capacity=capacity, projector_availability=projector)
        return redirect('room-list')


class RoomListView(View):
    def get(self, request):
        rooms = ConferenceRoom.objects.all()
        # for room in rooms:
        #     reservation_dates = [reservation.date for reservation in room.reservation_set.all()]
        #     room.reserved = datetime.date.today() in reservation_dates
        return render(
            request,
            'reservation_app/rooms.html',
            {'rooms': rooms}
        )


class DeleteRoomView(View):
    def get(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        room.delete()
        return redirect('room-list')
