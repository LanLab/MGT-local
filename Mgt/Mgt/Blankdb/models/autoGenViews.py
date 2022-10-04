from django.db import models
from .defModels import *
from .autoGenAps import *
from .autoGenCcs import *

class View_apcc(models.Model):
	class Meta:
		managed = False