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
import time
import csv,json
# Create your views here.


"""##############################################################################"""
"""------------------------------Page render-------------------------------------"""
"""##############################################################################"""
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
	#add an new unit 
	state=""
	if req.method=="POST":
		dd = req.POST['date']
		time = req.POST['time']
		topic = req.POST['topic']
		speaker = req.POST['speaker']
		thisYear = datetime.today().year
		date = str(thisYear)+ "-"+dd.replace("/","-")
		try:
			d = datetime.strptime(date, '%Y-%m-%d')
			unit(title=topic,speaker=speaker, pub_date=d,time=time).save()
		except:
			state= "plz check ur data fromat before submission!!"
	unit_list = unit.objects.all()
	context = {'list':unit_list,'state':state}
	return render(req,"index.html",context)

@login_required(login_url='/login')
def signature(req,unit_id):
	u = unit.objects.filter(pk=unit_id).get()
	today = datetime.strftime(datetime.now(), '%Y-%m-%d')
	unit_date = datetime.strftime(u.pub_date.date(), '%Y-%m-%d')
	if today == unit_date:
		x = str(int(str(u.time).split("-")[0].split(":")[0])+1)
		s_exist = participate.objects.filter(ref_unit=unit_id).exists()

		if s_exist:
			p = participate.objects.all().order_by("-sig_time")[:1].get()
			s = student.objects.filter(pk=p.ref_std.pk).get()
			context = {'timestamp':p.sig_time,'s_id':s.s_id,'class':s.c_g,'name':s.name,'pic':s.pic,"state_change":x+":00 之後算簽退"}
		else:
			context ={'state': " No records found","state_change":x+":00,之後算簽退"}
		return render(req,"signature.html",context )
	else:
		context = {'course':u.title,'date':u.pub_date}
		return render(req,"403.html",context)

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
		return render_to_response('std_search.html',{'state':'請輸入學生姓名，或者學號'})

@login_required(login_url='/login')
def create(req):
	s= student.objects.all().order_by("s_id")
	context = {
		'student':s
	}
	return render_to_response('create.html',context)

@login_required(login_url='/login')
def visualize(req):
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



"""##############################################################################"""
"""------------------------------Operating Method--------------------------------"""
"""##############################################################################"""
### ignore this function
def timeDef(base_in, now):
	delta_now = timedelta(hours=now.hour,minutes=now.minute)
	base_in = base_in.split("-")[0]
	delta_in = timedelta(hours=int(base_in.split(":")[0])+1)
	#sigin in check :
	diff =  str(delta_now - delta_in).split(":")[0]
	if diff >0:
		return "signout"
	else:
		return "signin"


def remove_unit(req):
	state="Delete Success ~ :D"
	try:
		pk = req.POST['pk']
		unit.objects.filter(pk=pk).delete()
	except:
		state="Delete Error!!"
	unit_list = unit.objects.all()
	context = {'list':unit_list,'state':state}
	return render(req,"index.html",context)


def scan_sign(req):
	if req.is_ajax():
		unit_id =req.POST['unit']
		card_id =req.POST['card_id']
		u = unit.objects.filter(pk=unit_id).get()
		base_sigin = str(u.time.split("-")[0])
		base_sigout = str(u.time.split("-")[1])
		now = datetime.today()
		state = timeDef(u.time, now)
		s_exist = student.objects.filter(card=card_id).exists()
		if s_exist:
			s = student.objects.filter(card=card_id).get()
			try:
				p = participate(ref_unit = u , ref_std = s,sig_time = now,state = state)
				p.save()
			except :
				return HttpResponse('Card id signature failed')		
		else:
			s_exist2 = student.objects.filter(s_id__iexact=card_id).exists()
			if s_exist2:
				try:
					s = student.objects.filter(s_id__iexact=card_id).get()
					p = participate(ref_unit = u , ref_std = s,sig_time = now,state = state)
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
	#### change card number

	if req.is_ajax():
		card_id =req.POST['number']
		std =int(req.POST['user'])
		s_exist = student.objects.filter(pk=std).exists()
		if s_exist:
			s = student.objects.filter(pk=std).get()			
			try:
				s.card = card_id
				s.save()
			except :
				return HttpResponse('update error by this student user')
			return HttpResponse('success')
		else:
			return HttpResponse('User does not exist.')
	else:
		return HttpResponse('ajax error')
