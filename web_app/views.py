#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core import serializers #json serialize
from django.utils import timezone
from web_app.form import uploadForm
from web_app.models import unit,participate,student
from datetime import datetime,timedelta
import datetime
import time
import csv,json
# Create your views here.


"""##############################################"""
"""--------------Page render---------------------"""
"""##############################################"""
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
def dblist(req):
	if req.method == "POST":
		return render_to_response('unit_management.html', {'form':upfm,'state':state})
	else:
		std = student.objects.all()
		p_count = participate.objects.count()
		p = {'std':std,'p_count':p_count}
	return render(req,"dblist.html",p)

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

def std_search(req):
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
		return render_to_response('std_search.html',{'state':'Please input student name'})

@login_required(login_url='/login')
def create(req):
	s= student.objects.all()
	context = {
		'student':s
	}
	return render_to_response('create.html',context)

"""##############################################"""
"""-------------Operating Method-----------------"""
"""##############################################"""

def timeDef(base_in,base_out,now):
	now = datetime.datetime.today()
	delta_now = datetime.timedelta(hours=now.hour,minutes=now.minute)

	delta_in = datetime.timedelta(hours=int(base_in.split(":")[0]),minutes=int(base_in.split(":")[1]))
	delta_out = datetime.timedelta(hours=int(base_out.split(":")[0]),minutes=int(base_out.split(":")[1]))
	#sigin in check :
	timecheck_in = str(abs(delta_now - delta_in)).split(":")
	timecheck_out = str(abs(delta_now - delta_out)).split(":")
	check = False
	if int(timecheck_in[0])<=0:
		if int(timecheck_in[1])<=60:
			check = True
			return "signin"
	if int(timecheck_out[0])<=0:
		if int(timecheck_out[1])<=60:
			check = True
			return "signout"
	if check == False:
		return "warning !!! "



def ajax_up_fb(req):	#upload fb audio file first,and return audio url path !
	name = req.POST['haha']
	print name
	return HttpResponse('not post')


def scan_sign(req):
	if req.is_ajax():
		unit_id =req.POST['unit']
		card_id =req.POST['card_id']
		u = unit.objects.filter(pk=unit_id).get()
		base_sigin = str(u.time.split("-")[0])
		base_sigout = str(u.time.split("-")[1])
		now = datetime.datetime.today()
		s_exist = student.objects.filter(card=card_id).exists()
		if s_exist:
			s = student.objects.filter(card=card_id).get()
			try:
				sign_state = timeDef(base_sigin,base_sigout,now)
				p = participate(ref_unit = u , ref_std = s,sig_time = now,state = sign_state)
				p.save()
				p = participate(
					ref_unit = u, 
					ref_std = s,
					sig_time = now,
					state = sign_state
				).save()
			except :
				return HttpResponse('Card id signature failed')		
		else:
			s_exist2 = student.objects.filter(s_id__iexact=card_id).exists()
			if s_exist2:
				try:
					s = student.objects.filter(s_id__iexact=card_id).get()
					sign_state = timeDef(base_sigin,base_sigout,now)
					p = participate(ref_unit = u , ref_std = s,sig_time = now,state = sign_state)
					p.save()
				except:
					return HttpResponse('Student id signature failed')		
			else:
				return HttpResponse('Card number can\'t find mapping student.')	
		try:
			record =  participate.objects.all().order_by('-pk')[:1].get()
			context={
				'name':s.name,
				'class':s.c_g,
				'sid':s.s_id,
				'pic':s.pic,
				'timestamp':record.sig_time.strftime('%Y-%m-%d %H:%M'),
				'state':record.state,
			}
			return HttpResponse(json.dumps(context),mimetype="application/json")
		except :
			return HttpResponse('User informaiton failed')
			
	else:
		return HttpResponse('Http is not  ajax post ')

	

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

def particple_records(req):
	#if req.method=="POST":
	p_list = participate.objects.all().order_by('-ref_unit')
	records= []
	for p in p_list:
		try:
			u = unit.objects.filter(pk=p.ref_unit.id).get()
			std = student.objects.filter(pk=p.ref_std.id).get()
			tmp ={
				'participate':str(p.sig_time).split('.')[0],
				'unit':u.title,
				'std':std.name,
				'sid':std.s_id
			}
			records.append(tmp)
		except:
			pass
	data = json.dumps({
		'p_list': records,
	})
	return HttpResponse(data, content_type='application/json')
	#else:
	#	return HttpResponse("error")

def commit_fb(req):
	if req.is_ajax():
		card_id =req.POST['number']
		unit_id =req.POST['unit']
		vertify_user =int(req.POST['user'])
		unit_id =10
		u = unit.objects.filter(pk=unit_id).get()
		base_sigin = str(u.time.split("-")[0])
		base_sigout = str(u.time.split("-")[1])
		#s_exist = student.objects.filter(card=card_id).exists()
		now = datetime.datetime.today()
		sign_state = timeDef(base_sigin,base_sigout,now)
		s_exist = student.objects.filter(pk=vertify_user).exists()
		if s_exist:
			s = student.objects.filter(pk=vertify_user).get()
			try:
				p = participate(
					ref_unit = u, 
					ref_std = s,
					sig_time = now,
					state = sign_state
				).save()
				s.card = card_id
				s.save()
			except :
				return HttpResponse('Signature failed!')
				#### change card number
			try:
				record =  participate.objects.all().order_by('-pk')[:1].get()
				context={
					'name':s.name,
					'class':s.c_g,
					'sid':s.s_id,
					'pic':s.pic,
					'timestamp':record.sig_time.strftime('%Y-%m-%d %H:%M'),
					'state':record.state,
				}
				return HttpResponse(json.dumps(context),mimetype="application/json")
			except : 
				return HttpResponse('Get records error!!')
			
		else:
			return HttpResponse('User does not exist.')

	return HttpResponse('ajax error')