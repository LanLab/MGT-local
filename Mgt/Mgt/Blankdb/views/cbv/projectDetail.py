
from django.views.generic.detail import DetailView
from Blankdb.models import Project, Isolate, User, Tables_ap
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Blankdb.views.FuncsAuxAndDb import columns
from Blankdb.views.FuncsAuxAndDb.routeToRightRawQFn import isolateChoices
from django.http import Http404


from django.conf import settings
import glob

class ProjectDetailView(PermissionRequiredMixin, DetailView):

	model = Project
	template_name = "Blankdb/projectDetail.html"

	def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		(list_cols, list_tabAps, list_tabCcs) = columns.columns(True)
		(list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = isolateChoices()

		context['dirColsInfo'] = list_cols
		context['dirAps'] = list_tabAps
		context['dirCcs'] = list_tabCcs
		context['serverStatusChoices'] = list_serverStatus
		context['assignStatusChoices'] = list_assignStatus
		context['privStatusChoices'] = list_privStatus
		context['boolChoices'] = boolChoices
		
		# print ("Project id is " + self.kwargs['pk'])
		list_projApFns = getProjApFileForDownload(self.kwargs['pk'])
		context['projApFns'] = list_projApFns


		return context


	raise_exception = True
	def has_permission(self):
		try:
			if User.objects.filter(userId=self.request.user).count() > 0:

				if Project.objects.get(id=self.kwargs['pk']).user == User.objects.get(userId = self.request.user):
					return True

			return False
		except:
			raise Http404("Either page does not exist or you do not have permission to view this page!");


def getProjApFileForDownload(projId):
	dir_filesForDownload = getattr(settings,'FILES_FOR_DOWNLOAD')

	appName = Project._meta.app_label

	list_fns = glob.glob(dir_filesForDownload + appName + "_aps_" + projId + "_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt.tar.gz")


	return list_fns
