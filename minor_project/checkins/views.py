from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse 
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.http.response import StreamingHttpResponse
#from .camera import VideoCamera
from .models import *
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .resources import *
# Create your views here.
#def gen(camera):
	#while True:
		#frame = camera.get_frame()
		#yield (b'--frame\r\n'
				#b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#def video_feed(request):
	#return StreamingHttpResponse(gen(VideoCamera()),content_type='multipart/x-mixed-replace; boundary=frame')

def homepage(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard"))
    return render(request, "checkins/homepage.html")

def form(request):

	if request.method == 'POST':
		form = InviteForm(request.POST ,request.FILES )
		name = request.POST["name"]
		email = request.POST["email"]
		event = request.POST["event"]
		img = request.FILES["img"]
		e = Checkins(name = name, email = email,event = event)
		i = Invites(name = name, email = email, event = event, img = img)
		if e is not None: 
			e.save()
		if form.is_valid():
			i.save()
			messages.success(request, "Invited Successfully")
			return render(request, "checkins/homepage.html",{
				"event_data": Event.objects.all().order_by('-date'),
			})
	else:
		form = InviteForm()
	
	return render(request, 'checkins/form.html', {
		"event_data": Event.objects.all().order_by('-date'),
		'invite_form' : form
	})

def dashboard(request):
	if request.user.is_authenticated:
		if request.method == "POST":
			title = request.POST["title"]
			date = request.POST["date"]
			amount = request.POST["amount"]
			description = request.POST["description"]
			user = request.POST["user"]
			e = Event(title = title, date = date, budget = amount, description = description, user = user)
			if e is not None: 
				e.save()
				messages.success(request, "Event Added Successfully" )
				return render(request, "checkins/nav/dashboard.html", {
					"event_data": Event.objects.all().order_by('-date'),
				})
		else:
			return render(request, "checkins/nav/dashboard.html", {
					"event_data": Event.objects.all().order_by('-date'),
				})
	else:
		return render(request, "checkins/homepage.html")

def edit_event(request, object_id):
	object = Event.objects.get(id = object_id)
	if request.method == "POST":
		object.title = request.POST["title"]
		object.date = request.POST["date"]
		object.budget = request.POST["amount"]
		object.description = request.POST["description"]
		if object is not None:
			object.save()
			messages.success(request, "Event Edited Successfully" )
			return render(request, "checkins/nav/dashboard.html", {
				"event_data": Event.objects.all().order_by('-date'),
            })
	else:
		return render(request, "checkins/nav/dashboard.html", {
			'form_data': object,
			"date": str(object.date),
			"event_data": Event.objects.all().order_by('-date'),
		})

def event_delete(request, object_id):
	object = Event.objects.get(id = object_id) 
	object.delete()
	messages.success(request, "Event Deleted Successfully" )     
	return render(request, "checkins/nav/dashboard.html", {
		"event_data": Event.objects.all().order_by('-date'),
	})

def delete_invite(request, object_id):
	cevent = ''
	current = []
	for e in Event.objects.all():
		if e.current:
			cevent = e.title
			break

	for i in Checkins.objects.all():
		if i.event == cevent:
			current.append(i)

	object = Checkins.objects.get(id = object_id) 
	object.delete()
	object = Invites.objects.get(id = object_id) 
	object.delete()
	messages.success(request, "Participant Deleted Successfully" )     
	return render(request, "checkins/nav/lists.html",{
		"invite_data": Checkins.objects.all().order_by('-event'),
		"current_invite_data": current,
	})

def live(request):
	return render(request, "checkins/nav/live.html")


def facereco(request):
	return render(request, "checkins/nav/facereco.html")

def lists(request):
	cevent = ''
	current = []
	for e in Event.objects.all():
		if e.current:
			cevent = e.title
			break

	for i in Checkins.objects.all():
		if i.event == cevent:
			current.append(i)

	return render(request, "checkins/nav/lists.html",{
		"current_invite_data": current,
		"invite_data": Checkins.objects.all().order_by('-event'),
	})

def profile(request):
	if request.method == "POST":
		n = request.POST["event"]
		object = Event.objects.get(pk = n)
		for i in Event.objects.all():
			i.current = False
			i.save()
		object.current = True
		object.save()
		messages.success(request, "Current Event set to " + object.title )
		return render(request, "checkins/nav/profile.html",{
			"events": Event.objects.all().order_by('-date'),
		})

	return render(request, "checkins/nav/profile.html",{
		"events": Event.objects.all().order_by('-date'),
	})

def statistics(request):
	return render(request, "checkins/nav/statistics.html")

def qr(request):
	return render(request, "checkins/nav/qr.html")

def qrscan(request):
	if request.method == "POST":
		n = request.POST["name"]
		object = Checkins.objects.get(pk = n)
		object.status = True
		if object.checkinType == "QR":
			object.checkinType = "QR" 
		elif object.checkinType == "FR":
			object.checkinType = "both"
		else:
			object.checkinType = "QR"
		object.save()
		messages.success(request, "Hello " + object.name )  
		# return render(request, "checkins/nav/qrscan.html")

	return render(request, "checkins/nav/qrscan.html")

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return HttpResponseRedirect(reverse("login"))
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request, "checkins/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return HttpResponseRedirect(reverse("dashboard"))
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "checkins/login.html", context={"login_form":form})

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "checkins/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000/chekins',
					'site_name': 'Self-Checkins',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return HttpResponseRedirect(reverse("password_reset_done"))
	password_reset_form = PasswordResetForm()
	return render(request, "checkins/password/password_reset.html", context={"password_reset_form":password_reset_form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return HttpResponseRedirect(reverse("homepage"))

import json
from django.forms.models import model_to_dict

class ChartData(APIView):
	authentication_classes = []
	permission_classes = []
	cevent = ''
	present = 0
	tcount=0
	frcount = 0
	qrcount=0
	bothcount=0

	def getpresent(self):
		for e in Event.objects.all():
			if e.current:
				self.cevent = e.title
				break
		for c in Checkins.objects.all():
			if c.status and c.event == self.cevent:
				self.present+=1
			if c.event == self.cevent:
				self.tcount+=1
			if c.event == self.cevent and c.checkinType == "FR":
				self.frcount+=1
			if c.event == self.cevent and c.checkinType == "QR":
				self.qrcount+=1 
			if c.event == self.cevent and c.checkinType == "both":
				self.bothcount+=1 

	def get(self, request, format=None):
		now = datetime.datetime.now()
		self.getpresent()
		data = {
            "event_data": Event.objects.values().order_by('-date'),
			"invite_data": Invites.objects.values().order_by('-event'),
			"checkins_data": Checkins.objects.values().order_by('-event'),

			"chart1": [self.present, self.tcount-self.present],
			"chart2": [self.frcount, self.qrcount, self.bothcount, self.tcount-self.qrcount-self.frcount-self.bothcount],
			# "got in": json.dumps(model_to_dict(Checkins.objects.get(name = 'divyam'))),
        }
		return Response(data)


def exportEvent(request):
    event_resource = EventResource()
    queryset = Event.objects.filter(user = request.user.username)
    dataset = event_resource.export(queryset)
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Events.xls"'
    return response

def exportInvites(request):
	event_resource = InvitesResource()
	cevent = ''
	current = []
	for e in Event.objects.all():
		if e.current:
			cevent = e.title
			break
	for i in Invites.objects.all().order_by('-event'):
			current.append(i)

	queryset = current
	dataset = event_resource.export(queryset)
	response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="Invites.xls"'
	return response

def exportCheckins(request):
	event_resource = CheckinsResource()
	cevent = ''
	current = []
	for e in Event.objects.all():
		if e.current:
			cevent = e.title
			break

	for i in Checkins.objects.all():
		if i.event == cevent:
			current.append(i)
	queryset = current
	dataset = event_resource.export(queryset)
	response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="Checkins.xls"'
	return response