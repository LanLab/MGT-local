
# from Salmonella.models import Project, User
from django.views.generic.edit import CreateView
import importlib
from django.urls import reverse

class CreateProjectView(CreateView):
	error_css_class = "errorlist"

	# model = Project
	fields = ['identifier'] #, 'user']
	# template_name = "Salmonella/projectCreate.html"
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
		print('project create for:', org)
		return ["Templates/projectCreate.html"]

	def get_success_url(self):
		org = self.kwargs.get('org')
		return reverse(f'{org}:project_detail', kwargs={'pk': self.object.id})


	def form_valid(self, form):
		"""Force the user to request.user"""
		org = self.kwargs.get('org')
		self.object = form.save(commit=False)
		userObj = createAndGetUser(self.request.user, org)
		self.object.user = userObj
		self.object.save()

		return super(CreateProjectView, self).form_valid(form)


def createAndGetUser(userId, org):
	Project, User = getModels(org)
	users = User.objects.filter(userId=userId)

	if users.count() == 0:
		user = User(userId=userId)
		user.save()

	user = User.objects.get(userId=userId)

	return user

	#if User.objects.filter(userId) == 0:
	#	user = User(userId=userId)

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Project = models.Project 
    User = models.User
    
    return Project, User