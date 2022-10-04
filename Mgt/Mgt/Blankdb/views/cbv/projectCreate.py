
from Blankdb.models import Project, User
from django.views.generic.edit import CreateView
from django.urls import reverse

class CreateProjectView(CreateView):
	error_css_class = "errorlist"

	model = Project
	fields = ['identifier'] #, 'user']
	template_name = "Blankdb/projectCreate.html"

	def get_success_url(self):
		return reverse('Blankdb:project_detail', kwargs={'pk': self.object.id})


	def form_valid(self, form):
		"""Force the user to request.user"""
		self.object = form.save(commit=False)
		userObj = createAndGetUser(self.request.user)
		self.object.user = userObj
		self.object.save()

		return super(CreateProjectView, self).form_valid(form)


def createAndGetUser(userId):

	users = User.objects.filter(userId=userId)

	if users.count() == 0:
		user = User(userId=userId)
		user.save()

	user = User.objects.get(userId=userId)

	return user

	#if User.objects.filter(userId) == 0:
	#	user = User(userId=userId)
