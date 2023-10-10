from django import forms
import importlib
# from .models import Location, Isolate, Isolation, Project, User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponseRedirect
from .FuncsAuxAndDb import queryDb as q
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from . import isolateForms_CreateEdit as isolateForms

def page(request, pk, org):
	Location, Isolate, Isolation, Project, User = getModels(org)
	# print(org)
	# CHECK: user has permission; if False <- send permission denied.
	if not has_permission(pk, request.user.username, org):
		raise PermissionDenied("Error: you dont have permission to edit this isolate.")

	isoObj = Isolate.objects.get(id=pk)

	if len(request.POST) == 0:

		form_iso = None
		form_loc = None
		form_isln = None
		
		# print ('The isQuery for this isolate is ' + str(isoObj.isQuery))
		if isoObj.isQuery == 't' or isoObj.isQuery == True:
			form_iso = create_isolate_form_no_priv(request.user, org, instance=isoObj)
		else:  
			form_iso = create_isolate_form(request.user, org, data=None, instance=isoObj)



		if isoObj.location:
			form_loc = isolateForms.create_location_form(org, instance=Location.objects.get(id=isoObj.location.id))
		else:
			form_loc = isolateForms.create_location_form(org)

		if isoObj.isolation:
			form_isln = isolateForms.create_isolation_form(org, instance=Isolation.objects.get(id=isoObj.isolation.id))
		else:
			form_isln = isolateForms.create_isolation_form(org)



		return render(request, 'Templates/isolateEdit.html', {'form_iso': form_iso, 'form_loc': form_loc, 'form_isln': form_isln, 'organism': org})

	if len(request.POST) > 0:
		form_iso = create_isolate_form(request.user, org, data=request.POST, instance=isoObj)

		if not isoObj.location:
			form_loc = isolateForms.create_location_form(org, request.POST)
		else:
			form_loc = isolateForms.create_location_form(org, request.POST, instance=Location.objects.get(id=isoObj.location.id))

		if not isoObj.isolation:
			form_isln = isolateForms.create_isolation_form(org, request.POST)
		else:
			form_isln = isolateForms.create_isolation_form(org, request.POST, instance=Isolation.objects.get(id=isoObj.isolation.id))

		if not form_iso.is_valid() or not form_loc.is_valid() or not form_isln.is_valid():

			return render(request, 'Templates/isolateCreate.html', {'form_loc': form_loc, 'form_iso': form_iso, 'form_isln': form_isln, 'organism': org})

		else:
			locObj = form_loc.save()
			islnObj = form_isln.save()

			isolateObj = form_iso.save(commit=False)
			# isolateObj.server_status = 'U' - dont update server status here.

			if locObj:
				isolateObj.location = locObj

			if islnObj:
				isolateObj.isolation = islnObj

			isolateObj.save()

		# print("process results: if any errors, resend form with errors; if all good, then reponse redirect")

	return HttpResponseRedirect(reverse(f'{org}:isolate_detail', kwargs={'pk': pk}))

def has_permission(pk, username, org):
	Location, Isolate, Isolation, Project, User = getModels(org)
	if User.objects.filter(userId=username).count() > 0: # if user exists
		if Isolate.objects.get(id=pk).project.user == User.objects.get(userId=username):
			return True

	return False

########################### ModelForms
def create_isolate_form(user, org, data, instance, *args, **kwargs): 
	Location, Isolate, Isolation, Project, User = getModels(org)
    
	class IsolateForm(forms.ModelForm): 
		class Meta:
			model = Isolate
			fields = ['identifier', 'privacy_status', 'project']
        
		def __init(self, user, *args, **kwargs): 
			super(IsolateForm, self).__init__(*args, **kwargs)

			self.fields['project'].queryset = Project.objects.filter(user=User.objects.get(userId=user))

	return IsolateForm(instance=instance, data=data, *args, **kwargs)

def create_isolate_form_no_priv(user, org, data, instance, *args, **kwargs): 
	Location, Isolate, Isolation, Project, User = getModels(org)
    
	class IsolateForm_noPriv(forms.ModelForm): 
		class Meta:
			model = Isolate
			fields = ['identifier', 'project']
        
		def __init(self, user, *args, **kwargs): 
			super(IsolateForm, self).__init__(*args, **kwargs)

			self.fields['project'].queryset = Project.objects.filter(user=User.objects.get(userId=user))

	return IsolateForm_noPriv(instance=instance, data=data, *args, **kwargs)
        

# Get models for a specific species 
def getModels(org): 
    models = importlib.import_module(f'{org}.models')
    Location = models.Location
    Isolate = models.Isolate
    Isolation = models.Isolation
    Project = models.Project
    User = models.User
    
    return Location, Isolate, Isolation, Project, User
