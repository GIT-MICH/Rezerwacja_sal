import datetime

from django.shortcuts import render, redirect
from django.views import View
from .models import ConferenceRoom, RoomReservation


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
        rooms = ConferenceRoom.objects.all().order_by('id')
        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = datetime.date.today() in reservation_dates
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


class ModifyRoomView(View):
    def get(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        return render(
            request,
            'reservation_app/modify_room.html',
            {'room': room}
        )

    def post(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        name = request.POST.get('room-name')
        capacity = request.POST.get('capacity')
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get('projector') == 'on'

        if not name:
            return render(
                request,
                'reservation_app/modify_room.html',
                {'room': room, 'error': 'Nie podano nazwy sali'}
            )
        if capacity <= 0:
            return render(
                request,
                'reservation_app/modify_room.html',
                {'room': room, 'error': 'Pojemność sali musi być dodatnia'}
            )
        if name != room.name and ConferenceRoom.objects.filter(name=name).first():
            return render(
                request,
                'reservation_app/modify_room.html',
                {'room': room, 'error': 'Sala o podanej nazwie istnieje'}
            )
        room.name = name
        room.capacity = capacity
        room.projector_availability = projector
        room.save()
        return redirect('room-list')


class ReservationView(View):
    def get(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(
            request,
            'reservation_app/reservation.html',
            {'room': room, 'reservations': reservations}
        )

    def post(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        date = request.POST.get('reservation-date')
        comment = request.POST.get('comment')
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')

        if RoomReservation.objects.filter(room_id=room, date=date):
            return render(
                request,
                'reservation_app/reservation.html',
                {'room': room, 'reservtions': reservations, 'error': 'Sala jest już zarezerwowana!'}
            )
        if date < str(datetime.date.today()):
            return render(
                request,
                'reservation_app/reservation.html',
                {'room': room, 'reservations': reservations, 'error': 'Data jest z przeszłości!'}
            )

        RoomReservation.objects.create(room_id=room, date=date, comment=comment)
        return redirect('room-list')


class RoomDetailsView(View):
    def get(self, request, room_id):
        room = ConferenceRoom.objects.get(id=room_id)
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(
            request,
            'reservation_app/room_details.html',
            {'room': room, 'reservations': reservations}
        )


class SearchView(View):
    def get(self, request):
        name = request.GET.get('room-name')
        capacity = request.GET.get('capacity')
        capacity = int(capacity) if capacity else 0
        projector = request.GET.get('projector') == 'on'

        rooms = ConferenceRoom.objects.all()
        if projector:
            rooms = rooms.filter(projector_availability=projector)
        if capacity:
            rooms = rooms.filter(capacity__gte=capacity)
        if name:
            rooms = rooms.filter(name__icontains=name)

        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = str(datetime.date.today() in reservation_dates)

        return render(
            request,
            'reservation_app/rooms.html',
            {'rooms': rooms}
        )

