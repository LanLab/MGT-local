from django.views.generic.base import TemplateView
from django_countries import countries

class IsoBulkUploadInst(TemplateView):

	template_name = "Blankdb/isoBulkUploadInst.html"

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
