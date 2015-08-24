#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core import serializers #json serialize
from django.utils import timezone
from web_app.models import unit,participate,student
from datetime import datetime
import view_processing

# Create your views here.
"""##############################################################################"""
"""------------------------------Render Pages--------------------------------"""
"""##############################################################################"""

def user_login(request):
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
	if req.method =="GET":
		unit_list = unit.objects.all().order_by("pub_date")
		context = {'list':unit_list}
	elif req.method == "POST":
		if req.POST['method'] == "PUT":
			pk = int(req.POST['pk'])
			u = unit.objects.filter(pk=pk).get()
			time = datetime.strptime(str(datetime.today().year)+"/"+
										req.POST['month']+"/"+
										req.POST['date']+
										" 10:10", "%Y/%m/%d %H:%M")
			u.pub_date = time
			u.speaker = req.POST['speaker']
			u.title = req.POST['topic']
			u.time = req.POST['time']
			u.save()
			return HttpResponse("ok")
		elif req.POST['method'] == "DELETE":
			pk =int(req.POST['pk'])
			unit.objects.filter(pk=pk).delete()
			return HttpResponse("ok")
		else:
			time = datetime.strptime(str(datetime.today().year)+"/"+
										req.POST['month']+"/"+
										req.POST['date']+
										" 10:10", "%Y/%m/%d %H:%M")
			
			unit(
				pub_date = time,
				speaker = req.POST['speaker'],
				title = req.POST['topic'],
				time = req.POST['time']
			).save()
			return HttpResponse("ok")
	return render(req,"index.html",context)

@login_required(login_url='/login')
def page_signature(req,unit_id):
	u = unit.objects.filter(pk=unit_id).get()
	today = datetime.strftime(datetime.now(),'%Y-%m-%d')
	unit_date = datetime.strftime(u.pub_date.date(), '%Y-%m-%d')
	if str(today) == str(unit_date):
		s_exist = participate.objects.filter(ref_unit=unit_id).exists()
		if s_exist:
			p = participate.objects.all().order_by("-sig_time")[:1].get()
			s = student.objects.filter(pk=p.ref_std.pk).get()
			context = {'timestamp':p.sig_time,'s_id':s.s_id,'class':s.c_g,'name':s.name,'pic':s.pic}
		else:
			context ={'state': " No records found"}
		return render(req,"signature.html",context )
	else:
		context = {'course':u.title,'date':u.pub_date}
		return render(req,"403.html",context)

@login_required(login_url='/login')
def page_sign_list(req,unit_id):
	p = participate.objects.filter(ref_unit=unit_id).order_by("-sig_time")
	context = {'list':p}
	return render(req,"list.html",context)

@login_required(login_url='/login')
def page_manage_menu(req):
	return render(req,"manage.html")

@login_required(login_url='/login')
def page_db_list(req):
	if req.method == "POST":
		return render_to_response('unit_management.html', {'form':upfm,'state':state})
	else:
		std = student.objects.all()
		p_count = participate.objects.count()
		p = {'std':std,'p_count':p_count}
	return render(req,"dblist.html",p)

def page_std_search(req):
	if req.method == "POST":
		key = req.POST['name']
		s_isExist = student.objects.filter(name=key).exists()
		if s_isExist:
			s= student.objects.filter(name=key).get()
			p = participate.objects.filter(ref_std=s)
			if p:
				return render_to_response('std_search.html', {'state':'search success.','list':p})
		else:
			sid_isExist = student.objects.filter(s_id__icontains=key).exists()
			if sid_isExist:
				s = student.objects.filter(s_id__icontains=key).get()
				p = participate.objects.filter(ref_std=s)
				return render_to_response('std_search.html', {'state':'search success.','list':p})
		return render_to_response('std_search.html', {'state':'no any records!!'} )
	else:
		#return render_to_response('std_management.html',{'state':'method is not post. please try again.'})	
		return render_to_response('std_search.html',{'state':'請輸入學生姓名，或者學號'})

@login_required(login_url='/login')
def page_fix_cardNumber(req):
	s = student.objects.all()
	context = {
		'student':s
	}
	return render_to_response('updateCard.html',context)

@login_required(login_url='/login')
def page_visualize_record(req):
	s= student.objects.all().order_by("s_id")
	units = unit.objects.all()
	std = student.objects.all().order_by("-s_id")
	result = {}
	for s in std:
		record = []
		participateTimes = 0
		for u in units:
			success = 0
			a = participate.objects.filter(ref_unit=u,ref_std=s,state="signin")
			if a.exists() :
				sin = a.count()
				success = success + 1
			else:
				sin = 0
			b = participate.objects.filter(ref_unit=u,ref_std=s,state="signout")
			if b.exists() : 
				sout = b.count()
				success = success + 1
			else:
				sout = 0
			if success == 2:
				participateTimes = participateTimes + 1
			record.append((sin,sout))
		record.append(participateTimes)
		result[s]=record
	context = {
		'list':result,
		'units':units
	}
	return render_to_response('visualize.html',context)
