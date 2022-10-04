
#replacefrom .autoGenAps import * # INITIALLY COMMENT THIS LINE
from django.db import models
from .isoMetaModels import *
import sys
from django.conf import settings
MEDIA_ROOT = settings.MEDIA_ROOT
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re
from django.core.validators import RegexValidator



class User(models.Model):
	userId = models.CharField(max_length=20, primary_key=True)

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.userId


def getIsolateFolderName(fn):
	arr = str(fn).split("/")

	arr.pop()

	path = MEDIA_ROOT + "/".join(arr)

	return path


	# def __str__(self):
	#    return self.id


# class Metadata(models.Model):
#    fieldname = models.FroeignKey()
#    value =


def getProjectFolderName(instance):
	db_table = str(instance._meta)
	appName = db_table.split(".", maxsplit=1)[0]

	return  MEDIA_ROOT + appName + "/" + instance.user.userId + "/" + str(instance.id)


class Project(models.Model):
	alphanumeric = RegexValidator(r'^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')


	identifier = models.CharField(max_length=50, verbose_name='Project', validators=[alphanumeric])

	user = models.ForeignKey(User, on_delete=models.PROTECT)

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("user", "identifier"))

	def __str__(self):
		return self.identifier


	def delete(self, *args, **kwargs):
		numIsolates = self.isolate_set.all().count()
		if numIsolates > 0:

			projDirName = getProjectFolderName(self)
			# print('is path!' + projDirName)


			# if os.path.exists(projDirName):
			# 	print ('deleting ' + projDirName)
			import shutil
			try:
				shutil.rmtree(projDirName)
			except:
				sys.stderr.write('Error: folder ' + str(projDirName) + " not found");


		super(Project, self).delete(*args,**kwargs)


def isolateUploadPath(instance, filename):
	db_table = str(instance._meta)
	appName = db_table.split(".", maxsplit=1)[0]
	# print("someone1")
	return  appName + "/" + instance.project.user.userId + "/" + str(instance.project.id) + "/" + str(instance.pk) + "/" + filename
	# 'user_{0}/{1}'.format(instance.user.id, filename)

def fastqGzValidator(value):
	if not (re.search(r'\.fastq\.gz$', str(value), flags=re.I) or re.search(r'\.fq\.gz$', str(value), flags=re.I)):
		raise ValidationError("File type should be .fastq.gz.")
	# print (value)

class Isolate(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	identifier = models.CharField(max_length=100, verbose_name='Isolate')
	# identifier and project together must be unique

	serovar = models.CharField(max_length=50, verbose_name='Serovar', blank=True, null=True)

	isQuery = models.BooleanField(verbose_name='Run as query', default=False)

	server_status_choices = (
		('U', 'Uploaded reads'),
		('V', 'Uploaded alleles'),
		('W', 'Uploaded assembly'),
		('I', 'In queue'),
		('R', 'Running reads to alleles'),
		('S', 'Running alleles to MGT'),
		('H', 'Holding'),
		('C', 'Complete'),
		('D', 'To download NCBI reads'),
		('A', 'Awaiting allele file'),
		('F', 'Error: incorrect file type')
	)

	privacy_status_choices = (
		('PU', 'Public'),
		('PV', 'Private'), # + 'UD' undefined
	)

	assignment_status_choices = (
		('A', 'Assigned MGT'),
		('F', 'Failed: contamination'),
		('G', 'Failed: genome quality'),
		('S', "Failed: serovar incompatibility"),
		('E', 'Error: other'),
	)

	privacy_status = models.CharField(
		max_length=2, choices=privacy_status_choices, verbose_name="Privacy status",
	)

	server_status = models.CharField(
		max_length=1, choices=server_status_choices, verbose_name="Server status",)

	assignment_status = models.CharField(
		max_length=1, choices=assignment_status_choices, blank=True, null=True, verbose_name="Assignment status",
	)

	file_forward = models.FileField(upload_to=isolateUploadPath, blank=True, null=True, max_length=500, validators=[fastqGzValidator], verbose_name="File forward")

	file_reverse = models.FileField(upload_to=isolateUploadPath, blank=True, null=True, max_length=500, validators=[fastqGzValidator], verbose_name="File reverse")

	file_alleles = models.FileField( upload_to=isolateUploadPath, blank=True, null=True, max_length=500, validators=[FileExtensionValidator([ 'fasta', 'fa'])], verbose_name="Alleles file")

	file_assembly = models.FileField(upload_to=isolateUploadPath, blank=True, null=True, max_length=1000, validators=[FileExtensionValidator([ 'fasta', 'fa', 'fna'])], verbose_name="Assembly file")

	tmpFn_alleles = models.CharField(max_length=50, blank=True, null=True, verbose_name="Expected file name")

	mgt1 = models.IntegerField(blank=True, null=True, verbose_name="MGT1 ST")

	#replacemgt = models.ForeignKey(Mgt, on_delete=models.PROTECT, blank=True, null=True) # INnameITIALLY COMMENT THIS LINE

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	# metadata = models.ManyToManyField() # TODO: store isolate metadata

	location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)
	isolation = models.ForeignKey(Isolation, on_delete=models.PROTECT, blank=True, null=True)
	extFks = models.ManyToManyField(ExternalFks)


	class Meta:
		unique_together = (("project", "identifier"),)
	# can two users have same project name and isolate name? (seems like they can...)


	def save(self):
		saved_fileForward = self.file_forward
		saved_fileReverse = self.file_reverse
		saved_fileAlleles = self.file_alleles
		saved_fileAssembly = self.file_assembly
		if not self.pk:

			self.file_forward = None
			self.file_reverse = None
			self.file_alleles = None
			self.file_assembly = None

			super(Isolate, self).save()

			self.file_forward = saved_fileForward
			self.file_reverse = saved_fileReverse
			self.file_alleles = saved_fileAlleles
			self.file_assembly = saved_fileAssembly

		super(Isolate, self).save()



	def delete(self, *args, **kwargs):

		# isolateDirName = getIsolateFolderName(self.file_forward)

		# self.file_forward.delete()
		# self.file_reverse.delete()
		print('In projModels: delete isolateFilePath')
		import shutil
		# rmdir the isolate_file_folder

		isolateFilePath = None

		if self.file_alleles:
			isolateFilePath = getIsolateFolderName(self.file_alleles)
		elif self.file_forward and self.file_reverse:
			isolateFilePath = getIsolateFolderName(self.file_forward)
		elif self.file_assembly:
			isolateFilePath = getIsolateFolderName(self.file_assembly)
		# print (isolateFilePath)
		try:
			print('Is it trying this....?')
			shutil.rmtree(isolateFilePath)
		except:
			sys.stderr.write("Error: folder " + str(isolateFilePath) + " not found");


		super(Isolate, self).delete(*args,**kwargs)

class Analysis_project(models.Model):
	identifier = models.CharField(max_length=50, verbose_name='project name')

	user = models.ForeignKey(User, on_delete=models.PROTECT)

	isolates = models.ManyToManyField(Isolate)

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.identifier
