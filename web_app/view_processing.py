#coding=utf-8
from django.shortcuts import render,get_object_or_404,HttpResponse,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from web_app.models import unit,participate,student
from datetime import datetime
from web_app.form import uploadForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import time
import csv,json

"""##############################################################################"""
"""------------------------------Operating Method--------------------------------"""
"""##############################################################################"""


#check whether have ever signed in before.
def checkStatus(unit, std, now):
	ro = participate.objects.filter(ref_unit = unit, ref_std = std, state = "signout").exists()
	if ro:
		return "今天已經完成簽到簽退，不要再刷了！！"
	ri = participate.objects.filter(	ref_unit = unit, ref_std = std, state = "signin").exists()
	print ro,ri
	if ri:
		r = participate.objects.filter(ref_unit = unit, ref_std = std, state = "signin").get()
		t_sig_time = datetime.strptime(str(r.sig_time).split("+")[0].split(".")[0], '%Y-%m-%d %H:%M:%S')
		t_now = datetime.strptime(str(now).split(".")[0], '%Y-%m-%d %H:%M:%S')

		if int(str(t_now - t_sig_time).split(":")[1]) >= 20:
			participate(ref_unit = unit, ref_std = std, sig_time = now, state = "signout").save()
		else:
			return "20分內已經簽到"
	else:
		participate(ref_unit = unit, ref_std = std, sig_time = now, state = "signin").save()


def op_scan_sign(req):
	if req.is_ajax():
		unit_id =req.POST['unit']
		card_id =req.POST['card_id']
		sign_state ="signin"
		u = unit.objects.filter(pk=unit_id).get()
		now = datetime.today()
		s_exist = student.objects.filter(card=card_id).exists()
		if s_exist:
			s = student.objects.filter(card=card_id).get()
			try:
				status = checkStatus(u, s, now)
				if status:
						return HttpResponse(status)			
			except :
				return HttpResponse('卡號有誤，刷卡失敗')		
		else:
			s_exist2 = student.objects.filter(s_id__iexact=card_id).exists()
			if s_exist2:
				s = student.objects.filter(s_id__iexact=card_id).get()	
				try:
					status = checkStatus(u, s, now)
					if status:
						return HttpResponse(status)			
				except:
					return HttpResponse('學號有誤，刷卡失敗')		
			else:
				return HttpResponse('找不到任何有關的學生資料，刷卡失敗')	
		try:
			record =  participate.objects.all().order_by('-pk')[:1].get()
			context = {
				'name':s.name,
				'class':s.c_g,
				'sid':s.s_id,
				'pic':s.pic,
				'timestamp':record.sig_time.strftime('%Y-%m-%d %H:%M'),
				'state':record.state,
			}
			return HttpResponse(json.dumps(context),mimetype="application/json")
		except :
			return HttpResponse('學生資料有問題，刷卡失敗')
			
	else:
		return HttpResponse('Http is not ajax post ')


def op_particple_records(req):
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

@login_required(login_url='/login')
def op_manage_unit(req):
	if req.method == "POST":
		upfm = uploadForm(req.POST, req.FILES) #blind
		if upfm.is_valid():
			model_type = req.POST['model_type']
			f= upfm.cleaned_data['upfile'].read()
			state = op_importFile(f,model_type)
			upfm = uploadForm()	
    		return render_to_response('unit_management.html', {'form':upfm,'state':state})
	else:
		upfm = uploadForm()
	return render_to_response('unit_management.html',{'form':upfm})


###  unit record
def op_importFile(file,model):
	if (model == "unit"):
		for row in csv.reader(file.splitlines()):
			try:
				timeS =  row[0]+" "+row[1].split("-")[0].replace("-",":")
				unit(title=(row[3]),
					 speaker=(row[4]),
					 description=(row[3]),
					 pub_date=(timeS),
					 time=(row[1])
				).save()
			except :
				return "something is wrong."
		return "success"
	else:
		for row in csv.reader(file.splitlines()):
			try:
				if row[0]!="":
					student(name=row[0],card=row[3],s_id=row[2],c_g=row[1] ,pic="").save()
			except :
				return "something is wrong."
		return "success"



def op_update_card(req):
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

def op_std_profile(req):
	if req.method == "POST":
		method = req.POST['method']
		if method != "POST":
			pk = int(req.POST['pk'])
		name = req.POST['name']
		num = req.POST['num']
		card = req.POST['card']
		s_class = req.POST['s_class']

		if method == "PUT":
			s = student.objects.filter(pk=pk).get()
			s.name = name
			s.card = card
			s.s_id = num
			s.c_g  = s_class
			s.save()
			return HttpResponse("ok")

		elif method == "DELETE":
			student.objects.filter(pk=pk).delete()
			return HttpResponse("ok")
		else:
			student(
				name = name,
				card = card,
				s_id = num,
				c_g  = s_class
			).save()
			return HttpResponse("ok")
	return render(req,"index.html",context)



def op_bacth(req):
	if req.method == "POST":
		username = User.objects.filter(pk=req.session['username']).get().username
		target = req.POST['target'].split(",")
		pwd = req.POST['password']
		user = authenticate(username=username, password=pwd)
		if user:
			for t in target:
				if t == "unit":
					unit.objects.all().delete()
				else:
					student.objects.all().delete()
			return HttpResponse("ok")
		else:
			return HttpResponse("wrong")