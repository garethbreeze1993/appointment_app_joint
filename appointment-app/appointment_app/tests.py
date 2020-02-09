import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient # similar to DjangoTest Client but used for REST API
from rest_framework.test import APITestCase # similar to django test case use when testing REST API
from rest_framework.test import APIRequestFactory 
# APIRequestFactory: This is similar to Django’s RequestFactory. It allows you to create requests with any http method, 
#which you can then pass on to any view method and compare responses.

from appointment_app.models import Times, Appointment
from appointment_app.serializers import AppointmentSerializer, TimesSerializer
from appointment_app.views import appointment_list, appointment_detail


def setup_user():
    User = get_user_model() # call the django user model via the get_user_model method
    return User.objects.create_user('test', email='test_user@gmail.com', password='test_pass') # create a user so I can login so I can get around permissions

def setup_user_2():
    User = get_user_model() # call the django user model via the get_user_model method
    return User.objects.create_user('new_user', email='new_user@gmail.com', password='new_pass') # create a user so I can login so I can get around permissions


class AppointmentAppModelTests(TestCase):
    
    def setUp(self):
        self.user = setup_user()
        self.time = Times.objects.create(time_start=datetime.time(9), date_start=datetime.date(2020, 1, 12))
        self.appointment = Appointment.objects.create(times=self.time, client=self.user) 
        
    
    def test_times_created(self):
        time_end_var = datetime.datetime.combine(datetime.date(2020, 1, 12), datetime.time(9))
        date_time_combined = timezone.make_aware(time_end_var)
        time_end_final = date_time_combined + datetime.timedelta(minutes=30)
        #self.time.save()
        self.assertEqual(self.time.time_start, datetime.time(9))
        self.assertEqual(self.time.date_start, datetime.date(2020, 1, 12))
        self.assertEqual(self.time.time_end, time_end_final)

    def test_appointment_created(self):
        self.assertEqual(self.time, self.appointment.times)
        self.assertTrue(self.appointment.filled)
        self.assertEqual(self.appointment.client, self.user)

class AppointmentAppViewTests(TestCase):
    
    def setUp(self):
        self.factory = APIRequestFactory() 
        self.uri = '/appointments/' # path to API endpoint
        self.uri_detail = '/appointments/1/'
        self.user = setup_user() # create a user at the start of every test so can call if needed
        self.client = APIClient()
        self.time = Times.objects.create(time_start=datetime.time(9), date_start=datetime.date(2020, 1, 12))
        self.appointment = Appointment.objects.create(times=self.time, client=self.user)
        
    def test_appointment_list_test_get_method(self):
        self.client.login(username='test', password='test_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 1))
        self.appointment_2 = Appointment.objects.create(times=self.time_2, client=self.user)
        response = self.client.get(self.uri) # call a get request object on api endpoint /appointment/
        self.assertEqual(response.status_code, 200, 'Expected Response Code 200, received {0} instead.'.format(response.status_code)) #<Response status_code=200, "text/html; charset=utf-8">
        self.assertEqual(len(response.data), 2) # should be 2 records one added in setup and 1 in test
        self.assertEqual(response.data[0].get('times')['date_start'], '2020-01-12')
        self.assertEqual(response.data[1].get('times')['date_start'], '2020-01-01')
        
    def test_appointment_list_test_get_method_not_authenticated_raise_403(self):
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 1))
        self.appointment_2 = Appointment.objects.create(times=self.time_2, client=self.user)
        request = self.factory.get(self.uri) # call a get request object on api endpoint /appointment/
        response = appointment_list(request)
        self.assertEqual(response.status_code, 403, 'Expected Response Code 403, received {0} instead.'.format(response.status_code)) 
        
    def test_appointment_list_test_post_method(self):
        self.client.login(username='test', password='test_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))
        self.json_string_appointment =  {
        "times": {
            "id": "2",
            "time_start": "11:00:00",
            "date_start": "2020-01-05"
        }
    }
        response = self.client.post(self.uri, self.json_string_appointment, format='json') # call a post request object on api endpoint /appointment/
        self.assertEqual(response.status_code, 201, 'Expected Response Code 201, received {0} instead.'.format(response.status_code))
        self.assertTrue(response.data['filled'])
        self.assertEqual(response.data['client'], 'test')
        self.assertEqual(response.data['times']['time_end'], '2020-01-05T11:30:00Z')
        
    def test_appointment_list_test_post_method_not_authenticated_raise_403(self):
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))
        self.json_string_appointment =  {
        "times": {
            "id": "2",
            "time_start": "11:00:00",
            "date_start": "2020-01-05"
        }
    }
        response = self.client.post(self.uri, self.json_string_appointment, format='json') # call a post request object on api endpoint /appointment/
        self.assertEqual(response.status_code, 403, 'Expected Response Code 201, received {0} instead.'.format(response.status_code))    
    
    def test_appointment_detail_test_get_method(self):
        self.client.login(username='test', password='test_pass')
        response = self.client.get(self.uri_detail)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['filled'])
        self.assertEqual(response.data['client'], 'test')
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['times']['time_end'], '2020-01-12T09:30:00Z')
        
    def test_appointment_detail_test_get_method_not_authenticated_raise_403(self):
        request = self.factory.get(self.uri_detail)
        response = appointment_detail(request)
        self.assertEqual(response.status_code, 403)    
        
    def test_appointment_detail_hit_except_condition_raise_404_error(self):
        self.client.login(username='test', password='test_pass')
        response = self.client.get('/appointments/21/')
        self.assertEqual(response.status_code, 404)
        
    def test_appointment_detail_test_delete_method(self):
        self.client.login(username='test', password='test_pass')
        response = self.client.delete(self.uri_detail)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.data)
     
    def test_appointment_detail_test_delete_method_not_authenticated_raise_403(self):
        response = self.client.delete(self.uri_detail)
        self.assertEqual(response.status_code, 403)
    
    def test_appointment_detail_test_put_method_time_filled_changed(self):    
        self.client.login(username='test', password='test_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))

        self.json_string_appointment =  {
        "id": "1",    
        "times": {
            "id": "2",
            "time_start": "11:00:00",
            "date_start": "2020-01-05"
        },
        "filled": "false"
        
    }
        response = self.client.put(self.uri_detail, self.json_string_appointment, format='json')
        self.assertEqual(response.status_code, 200) # {'id': 1, 'times': OrderedDict([('id', 2), ('time_start', datetime.time(11, 0)), ('time_end', '2020-01-05T11:30:00Z'), ('date_start', '2020-01-05')]), 'filled': False, 'client': 'test'}
        self.assertFalse(response.data['filled'])
        self.assertEqual(response.data['client'], 'test')
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['times']['time_end'], '2020-01-05T11:30:00Z')
        self.assertEqual(response.data['times']['time_start'], datetime.time(11, 0))
        self.assertEqual(response.data['times']['date_start'], '2020-01-05')
        self.assertEqual(response.data['times']['id'], 2)
        
    def test_appointment_detail_test_put_method_time_changed_filled_not_changed(self):    
        self.client.login(username='test', password='test_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))

        self.json_string_appointment =  {
        "id": "1",    
        "times": {
            "id": "2",
            "time_start": "11:00:00",
            "date_start": "2020-01-05"
        }        
    }
        response = self.client.put(self.uri_detail, self.json_string_appointment, format='json')
        self.assertEqual(response.status_code, 200) # {'id': 1, 'times': OrderedDict([('id', 2), ('time_start', datetime.time(11, 0)), ('time_end', '2020-01-05T11:30:00Z'), ('date_start', '2020-01-05')]), 'filled': False, 'client': 'test'}
        self.assertTrue(response.data['filled'])
        self.assertEqual(response.data['client'], 'test')
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['times']['time_end'], '2020-01-05T11:30:00Z')
        self.assertEqual(response.data['times']['time_start'], datetime.time(11, 0))
        self.assertEqual(response.data['times']['date_start'], '2020-01-05')
        self.assertEqual(response.data['times']['id'], 2)    
    
    def test_appointment_detail_test_put_method_time_not_changed_filled_changed(self):    
        self.client.login(username='test', password='test_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))

        self.json_string_appointment =  {
        "id": "1",   
        "times": {
            "id": "1",
            "time_start": "09:00:00",
            "date_start": "2020-01-12"
        },
        "filled": "false"
        
    }
        response = self.client.put(self.uri_detail, self.json_string_appointment, format='json')
        self.assertEqual(response.status_code, 200) # {'id': 1, 'times': OrderedDict([('id', 2), ('time_start', datetime.time(11, 0)), ('time_end', '2020-01-05T11:30:00Z'), ('date_start', '2020-01-05')]), 'filled': False, 'client': 'test'}
        self.assertFalse(response.data['filled'])
        self.assertEqual(response.data['client'], 'test')
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['times']['time_end'], '2020-01-12T09:30:00Z')
        self.assertEqual(response.data['times']['time_start'], datetime.time(9, 0))
        self.assertEqual(response.data['times']['date_start'], '2020-01-12')
        self.assertEqual(response.data['times']['id'], 1)
        
    def test_appointment_detail_test_put_method_client_changed(self):
        setup_user_2()
        self.client.login(username='new_user', password='new_pass')
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))

        self.json_string_appointment =  {
        "id": "1",   
        "times": {
            "id": "1",
            "time_start": "09:00:00",
            "date_start": "2020-01-12"
        },
        "filled": "false"
        }
        response = self.client.put(self.uri_detail, self.json_string_appointment, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['client'], 'new_user')
        
        
    def test_appointment_detail_test_put_not_authenticated_raise_403(self):    
        self.time_2 = Times.objects.create(time_start=datetime.time(11), date_start=datetime.date(2020, 1, 5))

        self.json_string_appointment =  {
        "id": "1",   
        "times": {
            "id": "1",
            "time_start": "09:00:00",
            "date_start": "2020-01-12"
        },
        "filled": "false"
        
    }
        response = self.client.put(self.uri_detail, self.json_string_appointment, format='json')
        self.assertEqual(response.status_code, 403) 
  
             
class AppointmentAppSerializerTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = setup_user()
    
    def test_time_serializer(self):
        time = Times.objects.create(time_start=datetime.time(9), date_start=datetime.date(2020, 1, 12))
        serialized_data = TimesSerializer(time).data # passing the time model object in to my seraializer
        time_date_start_string = time.date_start.strftime('%Y-%m-%d') # change to string so can test that the same data as serializer
        time_end_string = time.time_end.strftime('%Y-%m-%dT%H:%M:%SZ') # change to string so can test that the same data as serializer
        self.assertEqual(time.id, serialized_data['id'])
        self.assertEqual(time.time_start, serialized_data['time_start'])
        self.assertEqual(time_date_start_string, serialized_data['date_start'])
        self.assertEqual(time_end_string, serialized_data['time_end'])
        
    def test_appointment_serializer(self):
        self.client.login(username='test', password='test_pass')
        time = Times.objects.create(time_start=datetime.time(9), date_start=datetime.date(2020, 1, 12))
        time_end_string = time.time_end.strftime('%Y-%m-%dT%H:%M:%SZ') # change to string so can test that the same data as serializer
        appointment = Appointment.objects.create(times=time, client=self.user)
        serialized_data = AppointmentSerializer(appointment).data # passing the time model object in to my seraializer
        self.assertEqual(time_end_string, serialized_data['times']['time_end'])
        self.assertEqual(appointment.filled, serialized_data['filled'])
        self.assertEqual(appointment.client.username, serialized_data['client'])




        
        
        
        
        
        
        
