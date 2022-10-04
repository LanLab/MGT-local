import sys
import re
import os
from Bio import SeqIO
import readAppSettAndConnToDb


projectPath = input("path to MGT repo top folder: ")
projectPath = projectPath + "/Mgt/Mgt/"
settingtype = sys.argv[1]
username = input("Username of your new database first user: ")
email = input("email of your new database first user: " )
password = input("password of your new database first user: ")
projectName = ""
readAppSettAndConnToDb.setupEnvPath(projectPath, projectName,settingtype)

from django.contrib.auth.models import User
user=User.objects.create_user(username, password=password, email=email)
user.save()