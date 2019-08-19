from django.db import models
from django.utils.dateparse import parse_date
from datetime import date
import re
import bcrypt
import requests


class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        fname = postData['fname']
        lname = postData['lname']
        email = postData['email']
        username = postData['username']
        pw = postData['password']
        confirmpw = postData['confirmpassword']
        already_taken = User.objects.filter(username=username)
        if len(fname) < 3:
            errors['fname'] = 'First name should be at least 3 characters'
        if len(lname) < 3:
            errors['lname'] = 'Last name should be at least 3 characters'
        if len(username) < 2:
            errors['username'] = 'Username should be at least 2 characters'
        if len(already_taken) > 0:
            errors['username_taken'] = 'Username already taken, try again'
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors['email'] = 'Please enter a valid email address'
        if len(pw) < 8:
            errors['pword'] = 'Please enter a password greater than 7 characters'
        elif not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%_*?&])[A-Za-z\d@$!%_*?&]{3,}$", pw):
            errors['password'] = 'Please use a special character, one uppercase and one lowercase letter'
        if pw != confirmpw:
            errors['pwordmatch'] = 'Please make sure your passwords match!'
        return errors

    def login_validator(self, postData):
        errors = {}
        username = postData['username']
        password = postData['password']
        user_check = User.objects.filter(username=username)
        if len(user_check) < 1:
            errors['usernamenotfound'] = 'Username not in system'
        elif not bcrypt.checkpw(password.encode(), user_check[0].password.encode()):
            errors['passwordnotmatch'] = 'Password does not match records. Try again'
        return errors


class TripManager(models.Manager):
    def trip_validator(self, postData):
        errors = {}
        start_date_str = postData['startdate']
        end_date_str = postData['enddate']
        chosen_start_date = parse_date(start_date_str)
        chosen_end_date = parse_date(end_date_str)
        today = date.today()
        destination = postData['destination']
        plan = postData['plan']
        if len(start_date_str) == 0:
            errors["enterstartdate"] = "You must enter a date"
        if len(end_date_str) == 0:
            errors["enterenddate"] = "You must enter a date"
        elif chosen_start_date < today:
            errors["date"] = "Please enter date in the future"
        elif chosen_start_date > chosen_end_date:
            errors['invalid'] = "Your start date is after your end date, try again!"
        if len(destination) < 3:
            errors['destination'] = 'Destination must be greater than 2 characters'
        if len(plan) < 3:
            errors['plan'] = 'Plan must be greater than 2 characters'

        googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': postData['destination'],
            'sensor': 'false',
            'region': 'us',
            'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0'
        }
        req = requests.get(googlemapsapi, params=params)
        res = req.json()
        place_id = res['results'][0]['place_id']
        placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
        }
        req2 = requests.get(placesapi, params=params)
        res2 = req2.json()
        title = res2['result']['name']
        all_trips = Trip.objects.all()
        for trip in all_trips:
            if title == trip.title:
                errors['duplicate'] = "Trip already exists"
        return errors



class User(models.Model):
    first_name = models.CharField(max_length=90)
    last_name = models.CharField(max_length=90)
    username = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    password = models.CharField(max_length=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class Trip(models.Model):
    title = models.CharField(max_length=255)
    destination = models.CharField(max_length=90)
    plan = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    address = models.CharField(max_length=255)
    formatted_address = models.CharField(max_length=255)
    review = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    longitude = models.DecimalField(max_digits=8, decimal_places=4)
    latitude = models.DecimalField(max_digits=8, decimal_places=4)
    operating_hours = models.TextField(blank=True)
    website = models.CharField(max_length=255, default="Sorry, no website found")
    phone_number = models.CharField(max_length=20, default="Sorry, no phone number found")
    trip_host = models.ForeignKey(User, related_name='trips_hosted')
    user = models.ManyToManyField(User, related_name='users_trips')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TripManager()

