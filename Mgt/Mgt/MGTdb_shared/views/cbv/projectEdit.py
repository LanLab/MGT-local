
from django.views.generic import UpdateView
# from Salmonella.models import Project, User
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django import forms
import importlib


class ProjectUpdateView(PermissionRequiredMixin, UpdateView):

	# model = Project
	# template_name = "Salmonella/projectEdit.html"
	

	fields = ['identifier',]

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(**kwargs)
		context['organism'] = self.kwargs.get('org')
		return context

	def get_queryset(self):
		org = self.kwargs.get('org')
		Project, User = getModels(org)
		return Project.objects.all()
 
	def get_template_names(self):
		org = self.kwargs.get('org')
		print('project edit for:', org)
		return ["Templates/projectEdit.html"]

	def form_valid(self, form):
		org = self.kwargs.get('org')
		Project, User = getModels(org)
		if self.request.POST.get('identifier'):
			if (
				not form.cleaned_data['identifier'] or Project.objects.filter(identifier=self.request.POST.get('identifier'), user=User.objects.get(userId=self.request.user)).count() > 0
			):
				form.add_error('identifier', "Project name already exists. Please, pick another name.")
				return self.form_invalid(form)

		self.object = form.save()
		return HttpResponseRedirect(self.get_success_url())


	def get_success_url(self):
		org = self.kwargs.get('org')
		return reverse(f'{org}:project_detail', kwargs={'pk': self.object.id})


	raise_exception = True
	def has_permission(self):
		org = self.kwargs.get('org')
		Project, User = getModels(org)
		if User.objects.filter(userId=self.request.user).count() > 0:

			if Project.objects.get(id=self.kwargs['pk']).user == User.objects.get(userId = self.request.user):
				return True

		print(self.kwargs['pk'])
		return False

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Project = models.Project
    User = models.User
    
    return Project, User 