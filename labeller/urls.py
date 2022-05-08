"""Defines URL patterns for labeller"""
"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path, include, re_path
from . import views
urlpatterns = [

        path('add_note_to_slide', views.add_note_to_slide, name='add_note_to_slide'),
        path('add_tissue_type_to_slide/', views.add_tissue_type_to_slide, name='add_tissue_type_to_slide'),

    ############################################################################################
    ################################ URLS THAT SERVE HTML PAGES ################################

    ################################ base.html nav bar ################################

    re_path(r'^$', views.index, name='index'),

    re_path(r'^regions/$', views.regions, name='regions'),

    re_path(r'^slides/$', views.slides, name='slides'),

    re_path(r'^diagnoses/$', views.diagnoses, name='diagnoses'),

    # Page for viewing all projects created when uploading cells - under construction
    re_path(r'^projects/$', views.projects, name='projects'),

    # Page for viewing labelling stats/progress - under construction
    re_path(r'^stats/$', views.stats, name='stats'),

    ####################### other html pages (data labelling/export) #######################

    re_path(r'^project/(?P<project_id>\d+)/',
            views.project, name='project'),

    re_path(r'^diagnosis/(?P<diagnosis_id>\d+)/',
            views.diagnosis, name='diagnosis'),

    re_path(r'^all_cells_for_diagnosis/(?P<diagnosis_id>\d+)/',
            views.all_cells_for_diagnosis, name='all_cells_for_diagnosis'),

    re_path(r'^all_cells_for_diagnosis2/(?P<diagnosis_id>\d+)/',
            views.all_cells_for_diagnosis2, name='all_cells_for_diagnosis2'),

    re_path(r'^cell_redirect/(?P<cell_pk>\d+)/',
            views.cell_redirect, name='cell_redirect'),

    # Page for labelling a slide
    re_path(r'^label_slide/(?P<slide_id>\d+)/$',
            views.label_slide, name='label_slide'),

    # testpage for bootstrap
    re_path(r'^label_slide_bootstrap/(?P<slide_id>\d+)/$',
            views.label_slide, name='label_slide'),
    re_path(r'^bootstrap_test.html',
            views.bootstrap_test, name='bootstrap_test'),

    # Page for labelling a region of interest
    re_path(r'^label_region_fabric/(?P<region_id>\d+)/$',
            views.label_region_fabric, name='label_region_fabric'),

    # Not currently in use - may require fixing
    # Page for labelling a cell in given project
    re_path(r'^label_cells_in_project/(?P<project_id>\d+)/$',
            views.label_cells_in_project, name='label_cells_in_project'),

    # Page for exporting Project Data
    re_path(r'^export_project_data/$', views.export_project_data,
            name='export_project_data'),


    re_path(r'export_all_cell_annotations_for_user/$',
            views.export_all_cell_annotations_for_user, name='export_all_cell_annotations_for_user'),
    # Experimental
    # Page for exporting Project Data
    re_path(r'^export/', views.export_cell_data, name='export_cell_data'),

    re_path(r'^export_cells/$', views.export_all_cell_annotations_user,
            name='export_all_cell_annotations_user'),



    #******************************************************************************************#


    ################################################################################################
    ###################################### USER ACCOUNT HANDLING ###################################

    # Add Django site authentication URLS (login, logout, password management...)
    path('accounts/', include('django.contrib.auth.urls'), name='accounts'),

    # Add user registration page
    path('register/', views.register, name='register'),

    #******************************************************************************************#


    ########################################################################################################
    ############################################ AJAX FUNCTIONS ############################################
    re_path(r'^generic_ajax_get/', views.generic_ajax_get,
            name='generic_ajax_get'),

#***************************** ADD NOTES ***************************#
        # path('add_note_to_slide/', views.add_note_to_slide, name='add_note_to_slide'),
        # path('slides/add_note_to_slide/', views.CreateSlideNoteView.as_view(), name="add_note_to_slide"),
        # re_path(r'^add_note_to_slide/', views.CreateSlideNoteView.as_view(), name='add_note_to_slide'),
        # path('slides/get_slide_notes/', views.get_slide_notes, name='get_slide_notes'),
    re_path(r'^add_note_to_slide/', views.add_note_to_slide, name='add_note_to_slide'),
    #************************* SLIDE POSTS *************************#
    re_path(r'^add_diagnosis_to_slide/',
            views.add_diagnosis_to_slide, name='add_diagnosis_to_slide'),
    # Called remove and not delete because diagnosis is not deleted. It is just removed as a ManyToMany relation from slide
    re_path(r'^remove_diagnosis_from_slide/',
            views.remove_diagnosis_from_slide, name='remove_diagnosis_from_slide'),

    re_path(r'^get_number_of_slides_with_diagnosis_name/',
            views.get_number_of_slides_with_diagnosis_name, name='get_number_of_slides_with_diagnosis_name'),

    #************************* REGION POSTS *************************#
    re_path(r'^add_new_region/', views.add_new_region,
            name='add_new_region'),
    re_path(r'^delete_region/', views.delete_region, name='delete_region'),
    re_path(r'^toggle_region_complete_seg/',
            views.toggle_region_complete_seg, name='toggle_region_complete_seg'),
    re_path(r'^toggle_region_complete_class/',
            views.toggle_region_complete_class, name='toggle_region_complete_class'),

    #************************* PROJECT POSTS *************************#
    path('create_project', views.create_project, name="create_project"),




    #************************* CELL GETS *************************#
    re_path(r'^get_cell_feature_form/', views.get_cell_feature_form,
            name='get_cell_feature_form'),

    re_path(r'^get_cell_json/', views.get_cell_json, name='get_cell_json'),

    re_path(r'^get_all_cells_generic/', views.get_all_cells_generic,
            name='get_all_cells_generic'),

    re_path(r'^get_all_cells_in_project/',
            views.get_all_cells_in_project, name='get_all_cells_in_project'),

    re_path(r'^get_all_cells_in_slide/',
            views.get_all_cells_in_slide, name='get_all_cells_in_slide'),

    re_path(r'^get_all_cells_in_region/',
            views.get_all_cells_in_region, name='get_all_cells_in_region'),

    #************************* CELL AND CELLTYPE POSTS *************************#
    #re_path(r'^add_new_cell/', views.add_new_cell, name='add_new_cell'),

    # Add new cell with box (AJAX)
    re_path(r'^add_new_cell_box/', views.add_new_cell_box,
            name='add_new_cell_box'),
    re_path(r'^delete_cell/', views.delete_cell, name='delete_cell'),
    re_path(r'^change_cell_location/', views.change_cell_location,
            name='change_cell_location'),
    re_path(r'^update_cell_class/', views.update_cell_class,
            name='update_cell_class'),
    re_path(r'^add_additional_cellType_to_cell',
            views.add_additional_cellType_to_cell, name='add_additional_cellType_to_cell'),

    #******************************************************************************************#

    ####################################################################################
    ################################ DROPZONE UPLOADERS ################################
    # Handles uploaded cell images
    #path('dropzone_image', views.dropzone_image, name='dropzone_image'),
    #re_path(r'^label_cell_fabric/(?P<project_id>\d+)/dropzone_image', views.dropzone_image_w_projectID, name='dropzone_image_w_projectID'),
    re_path(r'^label_cells_in_project/(?P<project_id>\d+)/dropzone_image',
            views.dropzone_image_w_projectID, name='dropzone_image_w_projectID'),

    # Handles dropzone uploaded slides or slide spreadsheets
    #re_path(r'^label_cells_in_project/dropzone_slide', views.dropzone_slide, name='dropzone_slide_upload'),
    re_path(r'^slides/dropzone_slide', views.dropzone_slide,
            name='dropzone_slide_upload'),

    #***********************************************************************************#

        # CUSTOM ERROR PAGES
    path('403/', views.error_403, name='403_forbidden'),

]

# Show all cells
#	re_path(r'^cells2/$', views.cells2, name='cells2'),

# Page for labelling a slide
#	re_path(r'^label_slide_overlay/(?P<slide_id>\d+)/$', views.label_slide_overlay, name='label_slide_overlay'),

# Page for labelling a region of interest
#re_path(r'^label_region/(?P<region_id>\d+)/$', views.label_region, name='label_region'),

# # Page for exporting data
# re_path(r'^data_export/$', views.data_export, name='data_export'),

# Label next region
#	re_path(r'^next_region/', views.next_region, name='next_region'),

# # Change cell location (AJAX)
# re_path(r'^get_cell_center_relative_to_slide/', views.get_cell_center_relative_to_slide, name='get_cell_center_relative_to_slide'),

# Get cell information (AJAX)
#	re_path(r'^get_cellType/', views.get_cellType, name='get_cellType'),

# re_path(r'^blank_request/', views.blank_request, name='blank_request'),

# Page for labelling individual cell
# No longer in use - was for non-existed label_cell individual html page
#re_path(r'^label_cell/(?P<cell_id>\d+)/$', views.label_cell, name='label_cell'),

# Page for viewing Whole Slide IMages
#	re_path(r'^normal_cell_labeller/$', views.normal_cell_labeller, name= 'normal_cell_labeller'),

# Page for directly uploading cells enmasse.
# re_path(r'^upload_cells/$', views.upload_cells, name='upload_cells'),

# # Show all cells
# re_path(r'^cells/$', views.cells, name='cells'),

# # Add new region
# re_path(r'^new_region/$', views.new_region, name='new_region'),

# Page for viewing Whole Slide IMages
# re_path(r'^slide_viewer/$', views.slide_viewer, name= 'slide_viewer'),
