#import logging

# Get an instance of a logger
#log = logging.getLogger(__name__)
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from appointment_app.models import Times, Appointment
from appointment_app.permissions import IsOwnerOrReadOnly
from appointment_app.serializers import AppointmentSerializer,TimesSerializer
from django.core.mail import send_mail

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list(request, format=None):
    """
    List all code appointments, or create a new snippet.
    """
    if request.method == 'GET':
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client_id = request.user.id)
            send_mail('New Appointment',
                      f"Hello {request.user.username} you have booked an appointment on {request.data['times']['date_start']} at {request.data['times']['time_start']}",
                      'from@example.com',
                      [f'{request.user.email}'],
                      fail_silently=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOwnerOrReadOnly, IsAuthenticated])
def appointment_detail(request, pk, format=None):
    """
    Retrieve, update or delete a code appointment.
    """
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user)
            send_mail('Changed Appointment',
                      f"Hello {request.user.username} you have changed your appointment from  {appointment.times.date_start} at {appointment.times.time_start} to {request.data['times']['date_start']} at {request.data['times']['time_start']}",
                      'from@example.com',
                      [f'{request.user.email}'],
                      fail_silently=False)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        send_mail('Deleted Appointment',
                      f"Hello {request.user.username} you have deleted an appointment on {appointment.times.date_start} at {appointment.times.time_start}",
                      'from@example.com',
                      [f'{request.user.email}'],
                      fail_silently=False)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    


'''
request object on put method
{'times': {'id': 1, 'time_start': '09:00:00', 'date_start': '2020-01-07'}, 'filled': False}

1

'''

'''
send_mail('New Appointment',
                      f'Hello {request.user.username} you have booked an appointment on {request.data['times']['date_start']} at {request.data['times']['time_start']}',
                      'from@example.com',
                      [f'{request.user.email}'],
                      fail_silently=False)
'''

'''
https://docs.djangoproject.com/en/3.0/topics/email/
example post request json object to send
 {
        "times": {
            "time_start": "15:00:00",
            "date_start": "2020-01-03"
        },
        "filled": false
    }
'''

