#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers #json serialize
from django.utils import timezone
from web_app.form import uploadForm
from web_app.models import unit,participate,student

import time
import csv
# Create your views here.


"""##############################################"""
"""--------------Page render---------------------"""
"""##############################################"""
from django.shortcuts import render,redirect,render_to_response,HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def auth_vertify(request):
	if request.method == 'POST':
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				request.session['username'] = user.id #save session
				return HttpResponseRedirect('/')
			else:
				return render_to_response('login.html',{'msg':'error'})
		else:
			return render_to_response('login.html',{'msg':'error'})
	return render_to_response('login.html')

@login_required(login_url='/login')
def index(req):
	unit_list = unit.objects.all()
	context = {'list':unit_list}
	return render(req,"index.html",context)

@login_required(login_url='/login')
def signature(req,unit_id):
	s_exist = participate.objects.filter(ref_unit=unit_id).exists()
	if s_exist:
		p = participate.objects.all().order_by("-sig_time")[:1].get()
		u = unit.objects.filter(pk=p.ref_unit.pk).get()
		s = student.objects.filter(pk=p.ref_std.pk).get()
		context = {'timestamp':p.sig_time,'s_id':s.s_id,'class':s.c_g,'name':s.name,'pic':s.pic}
	else:
		context ={'state': " No records found"}
	return render(req,"signature.html",context )

@login_required(login_url='/login')
def list(req,unit_id):
	p = participate.objects.filter(ref_unit=unit_id).order_by("-sig_time")
	context = {'list':p}
	return render(req,"list.html",context)


@login_required(login_url='/login')
def manage(req):
	return render(req,"manage.html")


@login_required(login_url='/login')
def unit_management(req):
	if req.method == "POST":
		upfm = uploadForm(req.POST, req.FILES) #blind
		if upfm.is_valid():
			model_type = req.POST['model_type']
			f= upfm.cleaned_data['upfile'].read()
			state = importFile(f,model_type)
			upfm = uploadForm()	
			# return HttpResponseRedirect(reverse('upload:index'))
		# return HttpResponse('ok')
    		return render_to_response('unit_management.html', {'form':upfm,'state':state})
	else:
		upfm = uploadForm()
	return render_to_response('unit_management.html',{'form':upfm})

@login_required(login_url='/login')
def std_search(req):
	if req.method == "POST":
		key = req.POST['name']
		s_isExist = student.objects.filter(name=key).exists()
		if s_isExist:
			s= student.objects.filter(name=key).get()
			p = participate.objects.filter(ref_std=s)
			if p:
				return render_to_response('std_management.html', {'state':'search success.','list':p})
		else:
			sid_isExist = student.objects.filter(s_id__icontains=key).exists()
			if sid_isExist:
				s = student.objects.filter(s_id__icontains=key).get()
				p = participate.objects.filter(ref_std=s)
				return render_to_response('std_management.html', {'state':'search success.','list':p})
		return render_to_response('std_management.html', {'state':'no any records!!'} )
	else:
		#return render_to_response('std_management.html',{'state':'method is not post. please try again.'})	
		return render_to_response('std_management.html',{'state':'Please input student name'})


"""##############################################"""
"""-------------Operating Method-----------------"""
"""##############################################"""


@login_required(login_url='/login')
def scan_sign(req):
	if req.method == 'POST':
		card_id = req.POST['number']
		unit_id = req.POST['unit_id']
		try:
			u = unit.objects.filter(pk=unit_id).get()
			s_exist = student.objects.filter(card=card_id).exists()
			if s_exist :
				s = student.objects.filter(card=card_id).get()
				p = participate(ref_unit = u , ref_std = s)
				p.save()
			else:
				sid_exist = student.objects.filter(s_id=card_id).exists()
				if sid_exist:
					s = student.objects.filter(s_id=card_id).get()
					p = participate(ref_unit = u , ref_std = s)
					p.save()	
			return HttpResponseRedirect(reverse('web_app:signature', args=(int(unit_id),)))
		except:
			return HttpResponseRedirect(reverse('web_app:signature', args=(int(req.POST['unit_id']),)))
	else:
		return HttpResponse("ur method is not post")

@login_required(login_url='/login')
def importFile(file,model):
	if (model == "unit"):
		for row in csv.reader(file.splitlines()):
			try:
				timeS =  row[0]+" "+row[1].split("-")[0].replace("-",":")
				unit(title=row[4],speaker=row[3],description=row[4],pub_date=timeS,time=row[1]).save()
			except :
				pass
		return "success"
	else:
		for row in csv.reader(file.splitlines()):
			try:
				student(name=row[1],card=row[4],s_id=row[3],c_g=row[2] ,pic="").save()
			except :
				pass
		return "success"
                                                                                                                                                                                                                                                                                                                                                                                                                                                               