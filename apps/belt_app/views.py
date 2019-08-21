from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
import requests
from apps.belt_app.models import *
from random import randint




############ LOGIN AND REG ##################

#### REGISTER ####

def register(request):
    errors = User.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect("/login")
    else:
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        hashedpw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(first_name=fname, last_name=lname, username=username, email=email, password=hashedpw.decode())
        request.session['user_id'] = user.id
        return redirect("/home")


#### LOGIN/LOGOUT ####

def processlogin(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect ("/login")
    else: 
        user = User.objects.get(username=request.POST['username'])
        request.session['user_id'] = user.id
        return redirect("/home")


def loginpage(request):
    if "user_id" in request.session:
        return redirect("/home")
    else:
        return render(request, 'belt_app/loginpage.html')


def logout(request):
    del request.session['user_id']
    return redirect('/login')



#### ALL TRIPS AND MAP ####
def home(request):
    if "res1" not in request.session:
        request.session['res1'] = "Sorry no restaurants nearby"
        request.session['res2'] = ""
        request.session['res3'] = ""
    x = [request.session['res1'], request.session['res2'], request.session['res3']]
    if "user_id" not in request.session:
        return redirect('/login')
    else:
        current_user = User.objects.get(id=request.session['user_id'])
        context = {
            "nearby": x,
            'current_user': current_user,
            'users_trips': current_user.users_trips.all(),
            'all_trips': Trip.objects.all(),
            "sidebar_trips": Trip.objects.all().order_by("-id")[:10],
            "last_trip": Trip.objects.last(),
        }
        return render (request, 'belt_app/home.html', context)


#### DELETE A TRIP ####

def removetrip(request, num):
    user_id = request.session['user_id']
    curruser = User.objects.get(id=user_id)
    trip = Trip.objects.get(id=num)
    curruser.users_trips.remove(trip)
    return redirect('/home')

#### EDIT TRIP ####

def edittrip(request):
    errors = Trip.objects.trip_validator(request.POST)
    trip_id = request.POST['trip_id']
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect(f"trips/edit/{trip_id}")
    else:
        user_id = request.session['user_id']
        curruser = User.objects.get(id=user_id)
        trip = Trip.objects.get(id=trip_id)
        trip.destination = request.POST['destination']
        trip.plan = request.POST['plan']
        trip.start_date = request.POST['startdate']
        trip.end_date = request.POST['enddate']
        trip.save()
    return redirect('/home')


def edittriphome(request, num):
    user_id = request.session['user_id']
    curruser = User.objects.get(id=user_id)
    trip = Trip.objects.get(id=num)
    if curruser.id == trip.trip_host.id:
        context = {
            "trip": Trip.objects.get(id=num),
            'curruser': curruser,
        }
        return render(request, 'belt_app/edittriphome.html', context)
    else:
        return redirect("/home")



#### DELETE SOMETHING ####

def deletetrip(request, num):
    trip = Trip.objects.get(id=num)
    curruser = User.objects.get(id=request.session['user_id'])
    if curruser.id == trip.trip_host.id:  
        trip.delete()
        return redirect("/home")
    else: 
        return redirect('/home')





### VACATION METHODS ###
def create_trip(request):
    context = {
        "current_user" : User.objects.get(id=request.session["user_id"]),
        "all_trips": Trip.objects.all(),
        "sidebar_trips": Trip.objects.all().order_by("-id")[:10],
        "last_trip": Trip.objects.last(),
    }
    return render(request, 'belt_app/createtrip.html', context)


def process_create(request):
    errors = Trip.objects.trip_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags = key)
        return redirect("/home")
    else:
        # Google Maps API
        googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': request.POST['destination'],
            'sensor': 'false',
            'region': 'us',
            'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0',
        }
        req = requests.get(googlemapsapi, params=params)
        res = req.json()
        latitude = res['results'][0]['geometry']['location']['lat']
        longitude = res['results'][0]['geometry']['location']['lng']
        place_id = res['results'][0]['place_id']
        request.session['place_id'] = place_id

        # Google Places API
        placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
        }
        req2 = requests.get(placesapi, params=params)
        res2 = req2.json()
        title = res2['result']['name']
        try:
            x = len(res2['result']['reviews'])
        except:
            review_text = "No reviews yet"
        try:
            review_text = res2['result']['reviews'][randint(1,x)]['text']
        except:
            review_text = "No reviews yet"
        try:
            rating = res2['result']['rating']
        except:
            rating = 0
        try:
            phone = res2['result']['formatted_phone_number']
        except:
            phone = "No Phone number available"
        try:
            hours = res2['result']['opening_hours']['weekday_text']
        except:
            hours = "No hours available"
        formatted_address = res2['result']['formatted_address']
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        # Create the trip 
        new_trip = Trip.objects.create(
            title = request.POST['title'],
            destination=request.POST['destination'],
            plan=request.POST['plan'],
            start_date = request.POST['startdate'],
            end_date = request.POST['enddate'],
            address=request.POST['destination'],
            formatted_address=formatted_address,
            review=review_text,
            rating=rating,
            longitude=longitude,
            latitude=latitude,
            operating_hours=hours,
            phone_number=phone,
            trip_host=User.objects.get(id=request.session["user_id"])
        )
        new_trip.user.add(user)
        return redirect("/home")


def tripinfo(request, tripid):
    trip = Trip.objects.get(id=tripid)
    hours_str = trip.operating_hours #Get the string for place operating hours
    print(hours_str)
    if hours_str == "No hours available":
        left_bracket = "No hours listed"
        right_bracket= ""
        split_list = []
    else:
        split_list = hours_str.split(",") #Split the string into a list of strings, separated by commas

        #Replace [] and ' with empty string
        for word in split_list:
            if "[" in word:
                left_bracket = word.replace("[", "") #Only returns Monday without [
        for word in split_list:
            if "]" in word:
                right_bracket = word.replace("]", "") #Only returns Sunday without ]
        for word in split_list:
            if "'" in word:
                quotation = word.replace("'", "") #Not working
        
        split_list = split_list[1:-1]
    googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': Trip.objects.get(id=tripid).address,
        'sensor': 'false',
        'region': 'us',
        'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0'
    }
    req = requests.get(googlemapsapi, params=params)
    res = req.json()
    place_id = res['results'][0]['place_id']
    print(f"place id is {place_id}")
    placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
    }
    req2 = requests.get(placesapi, params=params)
    res2 = req2.json()
    try:
        photo0 = res2['result']['photos'][0]['photo_reference']
    except:
        photo0 = ""
    try:
        photo1 = res2['result']['photos'][1]['photo_reference']
    except:
        photo1 = ""
    try:
        photo2 = res2['result']['photos'][2]['photo_reference']
    except:
        photo2 = ""
    
    context = {
        "selected_trip": trip,
        'photo0': photo0,
        'photo1': photo1,
        'photo2': photo2,
        "split_hours" : split_list,
        "formatted_hours" : left_bracket,
        "formatted_hours2" : right_bracket,
    }
    return render(request, "belt_app/tripinfo.html", context)


def removeTrip(request, tripid):
    tripToDelete = Trip.objects.get(id = tripid)
    if request.session['user_id'] == tripToDelete.trip_host.id :
        tripToDelete.delete()
        return redirect('/home')
    else:
        return redirect('/home')




def apis(request, lat, long):
    nearby = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=15000&type=hotel&key=AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0"
    req = requests.get(nearby)
    res = req.json()
    print(res)

    try:
        request.session['res1'] = res['results'][0]['name']
    except:
        request.session['res1'] = "No restaurants nearby"
    try:
        request.session['res2'] = res['results'][1]['name']
    except:
        request.session['res2'] = ""
    try:
        request.session['res3'] = res['results'][2]['name']
    except:
        request.session['res3'] = ""

    return redirect("/home")
    
    