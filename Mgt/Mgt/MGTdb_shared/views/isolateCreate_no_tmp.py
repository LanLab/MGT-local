from django.shortcuts import get_object_or_404, render, redirect

def page(request, org):

	print(org)
	return render(request, 'Templates/isolateCreate_no_tmp.html', {"organism": org})
