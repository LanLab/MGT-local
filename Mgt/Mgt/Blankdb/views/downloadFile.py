import os
from django.conf import settings
from django.http import HttpResponse, Http404
from Blankdb.models import User, Project
from django.conf import settings
import re
from Blankdb.views.FuncsAuxAndDb import queryDb as q

def download(request, filename):
    appName = User._meta.app_label

    if re.match('^' + appName + "_aps_[0-9]{4}\-[0-9]{2}\-[-0-9]{2}\.txt\.tar\.gz$", filename):
        print ("Pattern matched - 1")

        return doTheDownload(filename)

    elif re.match('^' + appName + "_alleles_[0-9]{4}\-[0-9]{2}\-[-0-9]{2}\.tar\.gz$", filename):

        print ("Pattern matched - 2")

        return doTheDownload(filename)


    elif re.match('^' + appName + "_aps_[0-9]+_[0-9]{4}\-[0-9]{2}\-[-0-9]{2}\.txt\.tar\.gz$", filename):

        print ("Pattern matched - 3")

        if not request.user.is_authenticated:
            print ("User not authenticated");
            raise Http404('User not authenticated')
        # if extracted projectId not in user projIds

        else:
            req_projId = extractProjectId(filename)

            userProjIds = q.getUserProjectIds(request.user.username)
            # if User.objects.filter()

            if not int(req_projId) in userProjIds:
                raise Http404("This is not your project");

            else:

                return doTheDownload(filename)






    raise Http404('Requested file cannot be downloaded.')


def extractProjectId(filename):
    arr = filename.split("_")

    return arr[2]


def doTheDownload(filename):
    print("The path is " + filename)
    #path = './Blankdb/puFiles/' + filename
    # print("The path is " + path)

    file_path = settings.FILES_FOR_DOWNLOAD + filename

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/gzip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404("Unable to download file, please contact admins.")
