
from django.views.generic.edit import DeleteView
import importlib
# from Salmonella.models import Project, Isolate, User
from django.urls import reverse
#from django_tables2 import SingleTableMixin

from django.contrib.auth.mixins import PermissionRequiredMixin

class ProjectDeleteView(PermissionRequiredMixin, DeleteView):
	# model = Project
	# template_name = "Salmonella/projectDeleteConfirm.html"
	# success_url = "ProjectManagement/project_list"

	# table_class = IsolateTable
	# context_table_name = 'table'

	#def get_table_data(self):
	#	return [self.object]
	def get_queryset(self):
		org = self.kwargs.get('org')
		Project, Isolate, User = getModels(org)
		return Project.objects.all()
 
	def get_template_names(self):
		org = self.kwargs.get('org')
		print('project delete for:', org)
		return ["Templates/projectDeleteConfirm.html"]

	def get_context_data(self, **kwargs):
		org = self.kwargs.get('org')
		Project, Isolate, User = getModels(org)
		context = super().get_context_data(**kwargs)

		isolates = Isolate.objects.filter(project=self.object)

		context['isolates'] = isolates
		context['organism'] = org

		return context


	def get_success_url(self):
		org = self.kwargs.get('org')
		return reverse(f'{org}:project_list')

	raise_exception = True
	def has_permission(self):
		org = self.kwargs.get('org')
		Project, Isolate, User = getModels(org)
		if User.objects.filter(userId=self.request.user).count() > 0:

			if Project.objects.get(id=self.kwargs['pk']).user == User.objects.get(userId = self.request.user):
				return True

		print(self.kwargs['pk'])
		return False

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Project = models.Project
    Isolate = models.Isolate 
    User = models.User 
    
    return Project, Isolate, User
    