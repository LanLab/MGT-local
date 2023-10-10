from django.views.generic.base import TemplateView
from django_countries import countries

class IsoBulkUploadInst(TemplateView):

	# template_name = "Salmonella/isoBulkUploadInst.html"
 
	def get_template_names(self):
		org = self.kwargs.get('org')
		print('bulk upload for:', org)
		return render_to_response("Templates/isoBulkUploadInst.html", {"organism":org})
		# return ["Templates/isoBulkUploadInst.html"]


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['countries'] = list(countries)
		return context

"""
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['latest_articles'] = Article.objects.all()[:5]
    return context
"""
