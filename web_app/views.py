#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from web_app.models import unit,participate,student
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core import serializers #json serialize
from django.utils import timezone
import time
# Create your views here.


#page render
def index(req):
	unit_list = unit.objects.all()
	context = {'list':unit_list}
	return render(req,"index.html",context)

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
def list(req,unit_id):
	p = participate.objects.filter(ref_unit=unit_id).order_by("-sig_time")
	context = {'list':p}
	return render(req,"list.html",context)

#operating method


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


def manage(req):
	return render(req,"manage.html")