
from django.views.generic.edit import DeleteView
import importlib
from django.shortcuts import render
# from Salmonella.models import Isolate, User
from django.urls import reverse
#from django_tables2 import SingleTableMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

class IsolateDeleteView(PermissionRequiredMixin, DeleteView):
	# model = Isolate
	# template_name = "Salmonella/isolateDeleteConfirm.html"
	# success_url = "ProjectManagement/project_list"

	# table_class = IsolateTable
	# context_table_name = 'table'

	#def get_table_data(self):
	#	return [self.object]
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(**kwargs)
		context['organism'] = self.kwargs.get('org')
		return context

	def get_queryset(self): 
		org = self.kwargs.get('org')
		Isolate, User = getModels(org)
		return Isolate.objects.all()
	
	def get_template_names(self):
		org = self.kwargs.get('org')
		print('isolate delete for:', org)
		# return render(self.request, 'Templates/isolateDeleteConfirm.html', { "organism": org })
		return ["Templates/isolateDeleteConfirm.html"]


	def get_success_url(self):
		org = self.kwargs.get('org')
		return reverse(f'{org}:project_detail', kwargs={'pk': self.object.project.id})

	raise_exception = True
	def has_permission(self):
		org = self.kwargs.get('org')
		Isolate, User = getModels(org)
		if User.objects.filter(userId=self.request.user).count() > 0:

			if Isolate.objects.get(id=self.kwargs['pk']).project.user == User.objects.get(userId=self.request.user):
				return True

		print(self.kwargs['pk'])
		return False

def getModels(organism):
	models = importlib.import_module(f'{organism}.models')
	Isolate = models.Isolate
	User = models.User

	return Isolate, User