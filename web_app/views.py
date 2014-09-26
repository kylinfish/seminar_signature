#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core import serializers #json serialize
from django.utils import timezone
from web_app.form import UploadFileForm
from web_app.models import unit,participate,student
import time
import csv
# Create your views here.


"""##############################################"""
"""--------------Page render---------------------"""
"""##############################################"""

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

def manage(req):
	return render(req,"manage.html")

def unit_management(req):
	form = UploadFileForm(request.POST, request.FILES)
	return render(req,"unit_management.html",{'form':form})


"""##############################################"""
"""-------------Operating Method-----------------"""
"""##############################################"""



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



def import_unit(req):
	"""
	with open(path) as f:
		reader = csv.reader(f)
		for row in reader:
			a = unit(year=row[0],title=row[1],speaker=row[2],description=row[3],state=row[4],time=row[5]).save()
			print a
			"""
	return HttpResponse("123")


# Imaginary function to handle an uploaded file.

def import_unit(request):
	"""
    dataReader = csv.reader(open('/Users/viplab/Desktop/unit.csv'), delimiter=',', quotechar='"')
    for i,row in enumerate(dataReader):
    	if i!=0:
    		timeS =  row[0]+" "+row[1].split("-")[0].replace("-",":")
    		unit(title=row[4],speaker=row[3],description=row[4],pub_date=timeS ,time=row[1]).save()
	"""
	return render(request,"unit_management.html")
    #return render_to_response('upload.html', {'form': form})


