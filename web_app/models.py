# -*- coding: UTF-8 -*-
from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class unit(models.Model):
	title =  models.CharField(max_length=50)
	speaker = models.CharField(max_length=20)
	description = models.CharField(max_length=100,null=True,blank=True)
	state = models.BooleanField(default=False)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	time = models.CharField(max_length=30,null=True,blank=True)
	def __unicode__(self):
		return self.title



class student(models.Model):
	name = models.CharField(max_length=20)
	card = models.CharField(max_length=30)
	s_id = models.CharField(max_length=30)
	c_g = models.CharField(max_length=30,null=True,blank=True)#class and grade
	pic = models.CharField(max_length=60,null=True,blank=True)
	def __unicode__(self):
		return self.name


class participate(models.Model):
	ref_unit = models.ForeignKey(unit)
	ref_std = models.ForeignKey(student)
	sig_time = models.DateTimeField('date published', default=datetime.datetime.now)
	state = models.CharField(max_length=20)
	def __unicode__(self):
		seminar = unit.objects.filter(pk= self.ref_unit.pk).get()
		std = student.objects.filter(pk= self.ref_std.pk).get()
		return unicode(seminar.title)+" -- "+ unicode(std.name)+ " -- "+ unicode(self.sig_time)