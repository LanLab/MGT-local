from django.test import TestCase, RequestFactory 
from django.urls import reverse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User as u
from django.test.client import Client
from Vibrio.models import * 
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView
from views.cbv.projectList import ProjectListView
from views.cbv.projectCreate import CreateProjectView
from views.cbv.projectDetail import ProjectDetailView
from views.cbv.projectEdit import ProjectUpdateView
from views.cbv.projectDelete import ProjectDeleteView
from views.isolateDetail import page as isolate_detail_page



class TestViews(TestCase):
    databases = { 'default', 'vibrio' }

    def setUp(self):  
        
        # set up models 
        self.Vibrio_reference = Reference.objects.create(
            identifier = 'Vibrio',
            organism = '<i> Vibrio cholerae </i>',
            description = "['description']",
            date_created = '2019-07-25 11:02:11.642137+10',
            date_modified = '2022-08-17 07:51:35.10501+10'
        )

        # set up client and urls 
        self.client = Client()
        self.url_index = reverse('Vibrio:index')
        self.url_isolate_list = reverse('Vibrio:isolate_list')
        self.url_summary_report = reverse('Vibrio:summaryReport')
        
    def test_index_components(self): 
        response = self.client.get(self.url_index, using='vibrio')
        self.assertTemplateUsed(response, 'Templates/index.html')
        self.assertContains(response, '/vibrio/')
        self.assertContains(response, 'Database statistics:')
        self.assertContains(response, 'Publicly available data:')
        self.assertContains(response, 'Current trends - Top five MGT sequence types')
        

    def test_isolate_list_components(self):        
        response = self.client.get(self.url_isolate_list, using='vibrio')
        self.assertTemplateUsed(response, 'Templates/isolateList.html')
        self.assertTemplateUsed(response, 'Templates/isolateTable.html')
        self.assertContains(response, 'All isolates')
        self.assertContains(response, 'Filter isolates:')
        self.assertContains(response, 'Sequence types view')
        self.assertContains(response, 'Clonal complexes view')
        self.assertContains(response, 'Graphical view')
        
    
    def test_summary_report_components(self): 
        response = self.client.get(self.url_summary_report, using='vibrio')
        self.assertTemplateUsed(response, 'Templates/summaryReport.html')
        self.assertContains(response, 'Download a summary report')
        self.assertContains(response, 'Instructions')
        self.assertContains(response, 'Country')
        self.assertContains(response, 'Year start')
        self.assertContains(response, 'Year end')
        

class TestClassBasedViews(TestCase):
    databases = { 'default', 'vibrio' }
    
    def setUp(self): 
        self.factory = RequestFactory()
        self.client = Client()
        self.user = u.objects.create_user(username='vandana1408', password='random')
        self.client.login(username='vandana1408', password='random')
        
        self.db_user = User.objects.create(
            userId = "vandana1408",
            date_created = "2023-03-13 18:56:41.318937+11",
            date_modified = "2023-03-13 18:56:41.318964+11",
        )
        
        self.Vibrio_project = Project.objects.create(
            identifier = 'Vibrioproject',

            user = self.db_user,

            date_created = '2019-07-25 13:43:20.361359+10',
            date_modified = '2019-07-25 13:43:20.361373+10',
        )
        
        self.org = 'Vibrio'
                
    def test_project_list_components(self): 
        request = self.factory.get(reverse('Vibrio:project_list'),using='vibrio')
        request.user = self.user
        response = ProjectListView.as_view()(request, org=self.org)
        
        response.render()
        
        self.assertTemplateUsed('Templates/projectList.html')
        self.assertContains(response, 'My projects')
        self.assertContains(response, '+ Add new project')
        self.assertContains(response, 'Vibrioproject')
        
        
    def test_project_create_components(self): 
        request = self.factory.get(reverse('Vibrio:project_create'), using='vibrio')
        request.user = self.user 
        response = CreateProjectView.as_view()(request, org=self.org)
        
        response.render()
        
        self.assertTemplateUsed('Templates/projectCreate.html')
        self.assertContains(response, 'Create a new project')
        self.assertContains(response, 'Project:')
        
    def test_project_details_components(self): 
        request = self.factory.get(reverse('Vibrio:project_detail', args=[self.Vibrio_project.id]), using='vibrio')
        request.user = self.user 
        
        # print(request)
        response = ProjectDetailView.as_view()(request, pk=str(self.Vibrio_project.id), org=self.org)
        
        response.render()
        
        self.assertTemplateUsed('Templates/projectDetail.html')
        self.assertContains(response, 'Project details: Vibrioproject')
        self.assertContains(response, 'Isolates in this project')
        self.assertContains(response, '+ Upload a new isolate')
        self.assertContains(response, '+ Upload multiple isolates')
    
    def test_project_edit_components(self): 
        request = self.factory.get(reverse('Vibrio:project_edit', args=[self.Vibrio_project.id]), using='vibrio')
        request.user = self.user 
        
        response = ProjectUpdateView.as_view()(request, pk=str(self.Vibrio_project.id), org=self.org)
        
        response.render()
        
        self.assertTemplateUsed('Templates/projectEdit.html')
        self.assertContains(response, 'Edit project details')
        self.assertContains(response, 'Project:')
        self.assertContains(response, 'Vibrioproject')
        self.assertContains(response, 'Update')
    
    def test_project_delete_components(self): 
        request = self.factory.get(reverse('Vibrio:project_delete', args=[self.Vibrio_project.id]), using='vibrio')
        request.user = self.user 
        
        response = ProjectDeleteView.as_view()(request, pk=str(self.Vibrio_project.id), org=self.org)
        
        response.render()
        
        self.assertTemplateUsed('Templates/projectDeleteConfirm.html')
        self.assertContains(response, 'Are you sure you want to delete this project, and all its associated isolates?')
        self.assertContains(response, 'Project name')
        self.assertContains(response, 'Vibrioproject')
        self.assertContains(response, 'Confirm project delete')
    
    def test_isolate_create_components(self): 
        # request = self.factory.get(reverse('Vibrio:isolate_create'), using='vibrio')
        # request.user = self.user
        
        response = self.client.get(reverse('Vibrio:isolate_create'), using='vibrio')
        
        self.assertTemplateUsed('Templates/isolateCreate.html')
        self.assertContains(response, 'Create new isolate')
        self.assertContains(response, 'Location details')
        self.assertContains(response, 'Isolation details')
    
    # def test_isolate_create_bulkmd_components(self):
    #     response = self.client.get(reverse('Vibrio:isolate_create_bulk_md'), using='vibrio')
    #     response.user = self.user
        
    #     self.assertTemplateUsed('Templates/isolateCreateBulk_mdFile.html')
    #     self.assertContains(response, 'Upload multiple isolates')
    #     self.assertContains(response, 'Step 1. Download template')
    #     self.assertContains(response, 'Step 2. Upload metadata file')
    
    def test_isolate_create_bulkal_components(self):
        response = self.client.get(reverse('Vibrio:isolate_create_bulk_al', args=[self.Vibrio_project.id]), using='vibrio')
        
        self.assertTemplateUsed('Templates/isolateCreateBulk_alFiles.html')
        self.assertContains(response, 'Project: Vibrioproject')
        self.assertContains(response, 'Upload multiple allele files')
        self.assertContains(response, 'View project details')
    