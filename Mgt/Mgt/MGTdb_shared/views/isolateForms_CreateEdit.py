from django import forms
# from Salmonella.models import Location, Isolate, Isolation, Project, User
from .FuncsAuxAndDb import defaults
from django.core.validators import FileExtensionValidator
import importlib

def create_location_form(org, data=None, instance=None, *args, **kwargs):
	Location, Isolate, Isolation, Project, User = getModels(org)

	class LocationForm(forms.ModelForm):
		class Meta: 
			model = Location
			fields = ['continent', 'country', 'state', 'postcode']
			widgets = {
				'continent': forms.Select(attrs={'required':'true'}),
				'country': forms.Select(attrs={'required':'true'}),
			}

		def save(self):
			if isAllEmpty([self.instance.continent, self.instance.country, self.instance.state, self.instance.postcode]):
				return None

			locObj = getLocIfExists(self.instance.continent, self.instance.country, self.instance.state, self.instance.postcode, org)


			if not locObj:
				locObj = super().save(commit=True)

			return locObj

	return LocationForm(instance=instance, data=data, *args, **kwargs)

def isAllEmpty(list_):
	for val in list_:
		if val:
			return False

	return True


def getLocIfExists(continent, country, state, postcode, org):
	Location, Isolate, Isolation, Project, User = getModels(org)
	locObjs = Location.objects.filter(continent=continent, country=country, state=state, postcode=postcode)

	if len(locObjs) > 0: # if object already exists
		return locObjs.get()

	return None

def getIslnIfExists(source, type, host, disease, date, year, month, org):
	Location, Isolate, Isolation, Project, User = getModels(org)
	islnObjs = Isolation.objects.filter(source=source, type=type, host=host, disease=disease, date=date, year=year, month=month)

	if len(islnObjs) > 0:
		return islnObjs.get()

	return None



class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)
"""
class CheckboxInput(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(CheckboxInput, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(CheckboxInput, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)
"""

def create_isolation_form(org, data=None, instance=None, *args, **kwargs):
	Location, Isolate, Isolation, Project, User = getModels(org)
    
	class IsolationForm(forms.ModelForm):

		class Meta:
			model = Isolation
			fields = ['source', 'type', 'host', 'disease', 'date', 'year', 'month']
			widgets = {
				'date': forms.DateInput(attrs={'class':'datepicker'}),
				'year': forms.Select(attrs={'required':'true'}),
				'month': forms.Select(),
				'source': ListTextWidget(data_list=Isolation.objects.values_list('source').distinct(), name='source_list'),
				'host': ListTextWidget(data_list=Isolation.objects.values_list('host').distinct(), name='host_list'),
				'type': ListTextWidget(data_list=Isolation.objects.values_list('type').distinct(), name='type_list'),
				'disease': ListTextWidget(data_list=Isolation.objects.values_list('disease').distinct(), name='disease_list'),
			}


		# check date & year
		def clean(self):
			cleaned_data = super().clean()

			if 'date' in cleaned_data and 'year' in cleaned_data and cleaned_data['year'] and cleaned_data['date']:
				print ("both are supplied here")
				print(cleaned_data)

				if cleaned_data['date'] != None and cleaned_data['date'].year != cleaned_data['year']:
					raise forms.ValidationError('Error: Date\'s year and \'Collection year\' are not the same.')

			if 'date' in cleaned_data and 'month' in cleaned_data and cleaned_data['date'] and cleaned_data['month']:
				print ("both are supplied here again!")
				print(cleaned_data)

				if cleaned_data['date'] != None and cleaned_data['month'] != None and cleaned_data['date'].month != cleaned_data['month']:
					raise forms.ValidationError('Error: Date\'s month and \'Collection month\' are not the same. You can simply supply date, and \'Collection month\' will be extracted.')

			# print (cleaned_data)

		def save(self):
			if isAllEmpty([self.instance.source, self.instance.type, self.instance.host, self.instance.disease, self.instance.date, self.instance.year, self.instance.month]):
				return None

			if self.instance.date and not self.instance.year:
				self.instance.year = self.instance.date.year

			if self.instance.date and not self.instance.month:
				self.instance.month = self.instance.date.month

			islnObj = getIslnIfExists(self.instance.source, self.instance.type, self.instance.host, self.instance.disease, self.instance.date, self.instance.year, self.instance.month, org)


			if not islnObj:
				islnObj = super().save(commit=True)

			print("The isln object is")
			print(islnObj)

			return islnObj

	return IsolationForm(instance=instance, data=data, *args, **kwargs)

class IsolateMetaDataForm(forms.Form):
	project = forms.ModelChoiceField(queryset=None)
	file_md = forms.FileField( validators=[FileExtensionValidator(allowed_extensions=['csv'])])

	def __init__(self, user, org, *args, **kwargs):
		Location, Isolate, Isolation, Project, User = getModels(org) 
		super().__init__(*args, **kwargs)
		self.fields['project'].queryset = Project.objects.filter(user=User.objects.get(userId=user))


class IsolateCreateBulkForm(forms.Form):
	pass 
	# files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


def create_isolate_form_tmp(org, *args, **kwargs):
	Location, Isolate, Isolation, Project, User = getModels(org)

	class IsolateForm_tmp(forms.ModelForm):
		class Meta:
			model = Isolate
			fields = ['identifier', 'privacy_status',  'project', 'tmpFn_alleles', 'server_status']

	return IsolateForm_tmp(*args, **kwargs)



def create_IsoForm(user, org, *args, **kwargs):
	Location, Isolate, Isolation, Project, User = getModels(org)
	class IsolateForm(forms.ModelForm):

		class Meta:
			model = Isolate
			fields = ['identifier', 'privacy_status', 'file_forward', 'file_reverse', 'file_alleles', 'project', 'isQuery', 'file_assembly']
			widgets = {
				'isQuery': forms.CheckboxInput(attrs={'onclick':"javascript:showHideAssembly();"})
			}

		def __init__(self, user, *args, **kwargs):
			super(IsolateForm, self).__init__(*args, **kwargs)

			print (vars(self.fields['isQuery']))
			self.fields['project'].queryset = Project.objects.filter(user=User.objects.get(userId=user))

		# def clean(self):
			# pass 
			# cleaned_data = super().clean()
			"""
			print ('Cleaned data') 
			# print(cleaned_data.get('file_forward'))
			# print(cleaned_data.get('file_reverse'))

			# if no files are provided
			if isEmptyField('file_forward', cleaned_data) and isEmptyField('file_reverse', cleaned_data) and isEmptyField('file_alleles', cleaned_data) and isEmptyField('file_assembly', cleaned_data):  
				raise forms.ValidationError('Error: You must supply either 2 illumina reads files (forward and reverse), or alleles, extracted using the MGT pipeline. Alternatively, you can query an isolate  by providing eitther 2 Illumina reads files, or alleles, or an assembly, for MGT STs (where either an MGT-ST is assigned if it exists in the database or no assignment is made).')

			# if only one of the 2 illumina reads files is provided.
			if (not isEmptyField('file_forward', cleaned_data) and isEmptyField('file_reverse', cleaned_data)) or (isEmptyField('file_forward', cleaned_data) and not isEmptyField('file_reverse', cleaned_data)): 
				raise forms.ValidationError('Error: You must supply both illumina reads files.')

			# Provide exactly one type of file.

			if isEmptyField('file_forward', cleaned_data) and isEmptyField('file_reverse', cleaned_data): 
				if isEmptyField('file_alleles', cleaned_data) and isEmptyField('file_assembly', cleaned_data): 
				# if not ((cleaned_data['file_forward'] != None and cleaned_data['file_reverse'] != None and cleaned_data['file_alleles'] == None and cleaned_data['file_assembly'] == None) or (cleaned_data['file_forward'] == None and cleaned_data['file_reverse'] == None and cleaned_data['file_alleles'] != None and cleaned_data['file_assembly'] == None) or (cleaned_data['file_forward'] == None and cleaned_data['file_reverse'] == None and cleaned_data['file_alleles'] == None and cleaned_data['file_assembly'] != None)):
					raise forms.ValidationError('Error: please upload exactly one of either paired-end reads, alleles or assembly.')



			# if isQuery, then the isolate must be PV.
			if cleaned_data['isQuery'] == True and cleaned_data['privacy_status'] != 'PV':
				self.add_error('privacy_status', 'Please select \'Private\' if you wish to run your isolate in query mode.')
				raise forms.ValidationError('Error: if you choose to run your isolate as a query (i.e. \'Run as query\' is selected), then you must also set the privacy status to \'Private\' mode. We apologise for any inconvinience this causes.')
			"""

	return IsolateForm(user, *args, **kwargs)
			# print (cleaned_data)

def isEmptyField(key, cleaned_data): 
	if key not in cleaned_data or cleaned_data[key] == None: 
		return True

	return False

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Location = models.Location
    Isolate = models.Isolate
    Isolation = models.Isolation
    Project = models.Project
    User = models.User 
    
    return Location, Isolate, Isolation, Project, User