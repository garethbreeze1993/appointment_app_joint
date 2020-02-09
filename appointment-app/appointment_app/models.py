import datetime
import pytz
from django.db import models
from django.contrib import auth # built in django stuff for accounts
from django.contrib.auth.models import User
from django.utils import timezone

User._meta.get_field('email').blank = False

CHOICES_TIME_START = (
    (datetime.time(9), datetime.time(9)),
    (datetime.time(15), datetime.time(15)),
    (datetime.time(11), datetime.time(11)),
)


class Times(models.Model):
    
    '''
    class TimeChoices(datetime.time, models.Choices):
        NineAm = 9, '9AM'
        TenAm = 10, '10AM'
        ElevenAm = 11, '11AM'
    '''
    time_start = models.TimeField(choices=CHOICES_TIME_START)
    date_start = models.DateField()
    time_end = models.DateTimeField(editable=False)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['time_start', 'date_start'], name='unique_datetime')]
    
    def __str__(self):
        return f"Appointment from {self.time_start.strftime('%H:%M')} till {self.time_end.strftime('%H:%M') } on {self.date_start.strftime('%m-%d-%Y')}"
    
    def save(self, *args, **kwargs):
        date_time_combined = datetime.datetime.combine(self.date_start, self.time_start)
        date_time_combined = timezone.make_aware(date_time_combined)
        self.time_end = date_time_combined + datetime.timedelta(minutes=30)
        super().save(*args, **kwargs)
                
    

#class User(auth.models.User,auth.models.PermissionsMixin):
#	def __str__(self):
#		return "@{}".format(self.username)

class Appointment(models.Model):
    times = models.OneToOneField(Times, on_delete=models.CASCADE, related_name='times')
    filled = models.BooleanField(default=True)
    client = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='clients')

    
    def __str__(self):
        return f"Booked on {self.times} by {self.client}"


