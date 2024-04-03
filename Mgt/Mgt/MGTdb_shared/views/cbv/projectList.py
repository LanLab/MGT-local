from django.views.generic.list import ListView
# from Salmonella.models import Project, User
from django.db.models import Count
import importlib


class ProjectListView(ListView):
	# model = Project
	# template_name = "Salmonella/projectList.html"
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
		print('projects for:', org)
		return ["Templates/projectList.html"]
	
	def get_queryset(self):
		org = self.kwargs.get('org')
		# print('project list version',org)
		Project, User = getModels(org)
		if User.objects.filter(userId=self.request.user).count() > 0:
			userObj = User.objects.get(userId=self.request.user)

			return Project.objects.filter(user=userObj).annotate(isolate_count=Count('isolate'))
		else:
			return list()

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Project = models.Project
    User = models.User 
    
    return Project, User 