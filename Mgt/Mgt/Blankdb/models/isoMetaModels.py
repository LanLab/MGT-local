from django.db import models
from django_countries import countries
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

continent_choices = (
	('Africa', 'Africa'),
	('Antarctica', 'Antarctica'),
	('Oceania', 'Oceania'),
	('North America', 'North America'),
	('South America', 'South America'),
	('Europe', 'Europe'),
	('Asia', 'Asia'),
)

class Location(models.Model):

	continent = models.CharField(max_length=15, choices=continent_choices, blank=True, null=True, verbose_name="Continent")

	countryAbrev = list(countries)
	countryCountry = [(x[1],x[1]) for x in countryAbrev]
	country = models.CharField(max_length=75, choices=countryCountry, blank=True, null=True, verbose_name="Country")

	# country = CountryField(country_dict=True, blank=True, null=True)
	state = models.CharField(max_length=100, verbose_name="State or sub country", blank=True, null=True)
	postcode = models.IntegerField(blank=True, null=True, verbose_name="Postcode")

	class Meta:
		unique_together = (("continent", "country", "state", "postcode"),)


def month_choices():
	return [(r,r) for r in range(1,13)]

def year_choices():
    return [(r,r) for r in range(datetime.date.today().year, 1900, -1)]

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Isolation(models.Model):

	# source = models.CharField(max_length=100, blank=True, null=True)
	source = models.CharField(max_length=100, blank=True, null=True, verbose_name="Source")
	type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type")
	#host = models.CharField(max_length=100, blank=True, null=True)
	host = models.CharField(max_length=100, blank=True, null=True, verbose_name="Host")
	disease = models.CharField(max_length=120, blank=True, null=True, verbose_name="Host disease")
	# comments = models.TextField(blank=True, null=True)
	date = models.DateField(blank=True, null=True, verbose_name="Collection date")


	# year = models.IntegerField(blank=True, null=True, verbose_name="Collection year")
	year = models.IntegerField(choices=year_choices(), blank=True, null=True, verbose_name="Collection year")
	month = models.IntegerField(choices=month_choices(), blank=True, null=True, verbose_name="Collection month")

	class Meta:
		unique_together = (("source", "type", "host", "disease", "date", "month", "year"),)




class ExternalFks(models.Model):
	fkId = models.CharField(max_length=50)
	url = models.CharField(max_length=140, blank=True, null=True)
	name = models.CharField(max_length=50, verbose_name="Web resource name")

	class Meta:
		unique_together = (("fkId", "name"),)