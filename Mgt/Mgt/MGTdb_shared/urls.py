from django.urls import re_path as url, include
import re
from django.apps import apps
from django.views.generic import TemplateView
# from Mgt.settings_ import APPS_DATABASE_MAPPING as organisms
# from django.conf import settings.APPS_DATABASE_MAPPING as organisms
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
import MGTdb_shared.views as views
# from Mgt.urls_local_vp import urlpatterns 

urlpatterns = []
 
for org in settings.RAWQUERIES_DISPLAY: #organisms: 
    print('This is the organism!!!!!:', org)
    # view_module = __import__(f'{org}.views')
    # views = getattr(view_module, 'views')
    regex = '^[' + org[0].lower() + org[0] + ']' + org[1:]
    # print(regex)
    # print(views)
    
    new_patterns = [
            # url(r'^session/(?P<pk>[^/]+)$', views.sessionInfo.page, name='session_var'),
        url(r'^$', views.index.page, name='index'),

        url(r'^projects$', login_required(views.cbv.projectList.ProjectListView.as_view()), name="project_list"),
        url(r'^project-create$', login_required(views.cbv.projectCreate.CreateProjectView.as_view()), name='project_create'),
        url(r'^project-(?P<pk>\d+)-edit$', login_required(views.cbv.projectEdit.ProjectUpdateView.as_view()), name='project_edit'),
        url(r'^project-(?P<pk>\d+)-detail$', login_required(views.cbv.projectDetail.ProjectDetailView.as_view()), name='project_detail'),

        url(r'^bulkUploadInstructions$', login_required(views.isoBulkUploadInst.IsoBulkUploadInst.as_view()), name='instruction_bulkUpload'),

        url(r'^project-(?P<pk>\d+)-delete$', login_required(views.cbv.projectDelete.ProjectDeleteView.as_view()), name='project_delete'),
        # url(r'^isolate-(?P<pk>\d+)-detail$', login_required(views.cbv.isolateDetail.IsolateDetailView.as_view()), name="isolate_detail"), TODO: rename

        # url(r'^<org>/isolate-create-no-temporary', views.isolateCreate_no_tmp.page, name='isolate_create_no_tmp'),
        url(r'^isolate-list$', views.isolateList.page, name='isolate_list'),
        url(r'^isolate-create$', login_required(views.isolateCreate.page), name='isolate_create'),
        url(r'^isolate-createBmd$', login_required(views.isolateCreateBulk_mdFile.page), name='isolate_create_bulk_md'),
        url(r'^isolate-(?P<pk>\d+)-createBal$', login_required(views.isolateCreateBulk_alFiles.page), name='isolate_create_bulk_al'),

        url(r'^isolate-(?P<pk>\d+)-edit$', login_required(views.isolateEdit.page), name='isolate_create_bulk'),
        url(r'^isolate-(?P<pk>\d+)-edit$', login_required(views.isolateEdit.page), name='isolate_edit'),
        url(r'^isolate-(?P<pk>\d+)-delete$', login_required(views.cbv.isolateDelete.IsolateDeleteView.as_view()), name='isolate_delete'),
        url(r'^isolate-(?P<pk>\d+)-detail$', views.isolateDetail.page, name="isolate_detail"),


        url(r'^initial-isolates$', views.ajax.initialIsolates.page, name='initial_isolates'),
        url(r'^initial-projectIsolates$', login_required(views.ajax.initialProjectIsolates.page), name='initial_projectIsolates'),

        url(r'^search-projectDetail$', views.ajax.searchProjectDetail.page, name='search_projectDetail'),
        url(r'^search-isolateList$', views.ajax.searchIsolateList.page, name='search_isolateList'),
        url(r'^search-isolateDetail$', views.ajax.searchIsolateDetail.page, name='search_isolateDetail'),


        url(r'^top-st$', views.ajax.topStSummary.page, name='topStSummary'),



        url(r'^timeStCount$', views.ajax.graph_timeStCount.page, name='timeStCount'),
        url(r'^timeLocStCnt$', views.ajax.graph_timeLocStCnt.page, name='timeLocStCnt'),
        # url(r'^order-by$', views.ajax.orderBy_router.page, name='order_by'),


        url(r'^summaryReport$', views.summaryReport.page, name='summaryReport'),
        url(r'^getDataForReport$', views.ajax.report.page, name='reportData'),


        url(r'^downloadDbDump-(?P<filename>.*)$', views.downloadFile.download, name='downloadDbDump')
        # url(r'^create-isolate$', login_required(views.cbv.createIsolate.CreateIsolateView.as_view()), name='create_isolate'),
        # url(r'^create-isolate$', login_required(views.createIsolate.page), name='create_isolate'),
        # url(r'^isolate-(?P<pk>\d+)-edit$', login_required(views.cbv.editIsolate.IsolateUpdateView.as_view()), name='edit_isolate'),
    ]
    
    
    
    urlpatterns.append(url(f'{regex}/', include((new_patterns, str(org))), {'org': org}, name=org))
    
    

    # urlpatterns += new_patterns
    
# print(urlpatterns)    


