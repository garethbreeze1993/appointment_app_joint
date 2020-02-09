#import logging

# Get an instance of a logger
#log = logging.getLogger(__name__)
import datetime
from django.utils import timezone
from rest_framework import serializers
from appointment_app.models import Times, Appointment

CHOICES_TIME_START = (
    (datetime.time(9), datetime.time(9)),
    (datetime.time(15), datetime.time(15)),
    (datetime.time(11), datetime.time(11)),
)

class TimesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    time_start = serializers.ChoiceField(choices=CHOICES_TIME_START)
    class Meta:
        model = Times
        fields = ('id', 'time_start', 'time_end', 'date_start')
        
class UserSerializer(serializers.ModelSerializer):
    pass
        
        
class AppointmentSerializer(serializers.ModelSerializer):
    times = TimesSerializer()
    client = serializers.ReadOnlyField(source='client.username')
    class Meta:
        model = Appointment
        fields = ('id', 'times', 'filled', 'client')
        
    def create(self, validated_data):
        times_data = validated_data.pop('times')
        times_data_id = times_data['id']
        time = Times.objects.get(id=times_data_id)
        appointment = Appointment.objects.create(times=time, **validated_data)
        return appointment
    
    def update(self, instance, validated_data):
        times_data = validated_data.pop('times')
        instance.filled = validated_data.get('filled', instance.filled)
        instance.client = validated_data.get('client', instance.client)
        time_obj_id = times_data.get('id', instance.times.id)
        if instance.times.id != time_obj_id:
            times_obj = Times.objects.get(id=times_data.get('id'))
            instance.times = times_obj
            instance.save()
        else:
            instance.save()
        return instance

# https://www.youtube.com/watch?v=EyMFf9O6E60

# when doing put request it is going through but when doing get request it is just reverting back just for the times thing
# for this look at the id as my theory is if the id isn't bein chagned when doing get request will jus use the data
# related to that id

# Try doing datetime.time object as parameter on models choices
