from django.shortcuts import render
from django import forms
from django_countries.fields import CountryField
from . import isolateForms_CreateEdit as isolateForms
from Blankdb.models import Project, User, Tables_ap, Reference
import datetime

def page(request):

	if request.user.is_authenticated:
		form = downloadReportForm_auth(user=request.user.username);
	else:
		form = downloadReportForm()

	# list_countries = list(countries);

	numMgtLvls = Tables_ap.objects.filter(table_num=0).count()
	orgName = Reference.objects.all()[0].organism

	return render(request, 'Blankdb/summaryReport.html', {'form': form, 'numMgtLvls': range(numMgtLvls), 'orgName': orgName});

def year_choices():
    return [(r,r) for r in range(1984, datetime.date.today().year+1)]

def current_year():
    return datetime.date.today().year

def ten_years_ago():
    return datetime.date.today().year - 10 + 1

class downloadReportForm(forms.Form):

	country = CountryField().formfield()
	# yearStart = forms.IntegerField()
	# yearEnd = 
	year_start = forms.TypedChoiceField(choices=year_choices, initial=ten_years_ago, coerce=int) 
	year_end = forms.TypedChoiceField(choices=year_choices, initial=current_year, coerce=int)
	 #, default=current_year)
	
	"""
	widgets = {
		'country': forms.Select()
	}
	"""





class downloadReportForm_auth(forms.Form):
	def __init__(self, *args, **kwargs):
		self.username = kwargs.pop('user')
		super(downloadReportForm_auth, self).__init__(*args, **kwargs)
		# print("This is the username " + username);
		projData = list(Project.objects.filter(user=self.username).values_list('id', 'identifier'))
		projData.insert(0, ('', '----'))
		self.fields['project'].choices = projData

	# country = forms.CharField(label="Country", max_length=200)

	project = forms.ChoiceField(label="Project", required=False);
	country = CountryField().formfield(required=False)
	year_start = forms.TypedChoiceField(choices=year_choices, initial=ten_years_ago, coerce=int) 
	year_end = forms.TypedChoiceField(choices=year_choices, initial=current_year, coerce=int)
