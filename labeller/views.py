from distutils.log import error
from pdb import post_mortem
from urllib import request
from HL_site.settings import DATA_EXPORT_ROOT
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.core import serializers
from django.http import JsonResponse
import json
import os
from datetime import datetime
from django.db import models
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import login, authenticate

from django.contrib.auth.models import User
from django.views.generic import CreateView

from .models import Region, Cell, Slide, Project, CellType, Diagnosis
from .forms import UserForm, CellFeatureForm

from django.conf import settings
from django.conf.urls.static import static
from django.core.files import File
from django.core.files.images import ImageFile

import pandas as pd
import csv


def index(request):
    """The home page for labeller"""
    return render(request, 'labeller/index.html')


def export_cell_image(cell, cell_path, size):
    svs_path = settings.MEDIA_ROOT + cell.region.slide.svs_path.url
    left = cell.region.x + cell.center_x - size/2
    top = cell.region.y + cell.center_y - size/2
    command = "vips crop " + svs_path + " " + cell_path + " " + \
        str(left) + " " + str(top) + " " + \
        str(size) + " " + str(size)
    os.system(command)


def generate_cell_image_with_vips(region, cid, left, top, width, height):
    region_path = settings.MEDIA_ROOT + region.image.url
    cell_path = settings.MEDIA_ROOT + '/cells/' + str(cid) + '.jpg'
    # left = cell.region.x + cell.center_x - size/2
    # top = cell.region.y + cell.center_y - size/2

    command = "vips crop " + region_path + " " + cell_path + " " + \
        str(left) + " " + str(top) + " " + \
        str(width) + " " + str(height)
    os.system(command)

    # Old region-based method of cropping
    # cell = ct.cell
    # cell_path = cell_folder + str(cell.id) + '.jpg'
    # region_path = settings.MEDIA_ROOT + cell.region.image.url
    # left = cell.center_x - size/2
    # top = cell.center_y - size/2
    # command = "vips crop "+ region_path + " " + cell_path + " " + \
    # 	str(left) + " " + str(top) + " " + \
    # 	str(size) + " " + str(size)
    # os.system(command)


def export_all_cell_annotations_user(request):
    if (request.user.username != 'admin'):
        print('user access denied in export_all_cell_annotations_user')
        return JsonResponse({'success': False})

    export_path = settings.MEDIA_ROOT + '/export/'
    # export_path += datetime.now().strftime("%Y%m%d%H%M%S") + '/'
    # os.system('mkdir '+export_path)
    export_path = export_path+datetime.now().strftime("%Y%m%d%H%M%S")+'_cellTypes.csv'

    cellTypes = CellType.objects.filter(user=request.user)

    ct_names = cellTypes.values('cell_type').distinct()
    distinct_cell_types = CellType.objects.values_list(
        'cell_type', flat=True).distinct().order_by('cell_type')
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        outputRow = ['user', 'slides', 'regions', 'cells']
        for ct_name in distinct_cell_types:
            outputRow = outputRow + [getCellTypeNameFromStringCode(ct_name)]
        writer.writerow(outputRow)

        outputRow = [request.user.username,  Slide.objects.all().count(
        ), Region.objects.all().count(), Cell.objects.all().count()]
        for ct_name in distinct_cell_types:
            count = CellType.objects.filter(
                user=request.user, cell_type=ct_name).count()
            outputRow = outputRow + [count]
        writer.writerow(outputRow)

    return JsonResponse({'success': True})


def export_all_cell_annotations_for_user(request):
    cellTypes = CellType.objects.filter(
        user=request.user).order_by('cell_type')

    export_path = settings.MEDIA_ROOT + '/export/'
    export_path = export_path+datetime.now().strftime("%Y%m%d%H%M%S") + \
        '_all_cell_annotations_'+request.user.username+'.csv'

    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        outputRow = ['cell_id', 'annotation_code', 'annotation_name', 'region',
                     'slide', 'slide_diagnoses', 'annotator']
        writer.writerow(outputRow)
        # print(outputRow)

        # counter = 0

        for ct in cellTypes:
            dx_str = ''
            for dx in ct.cell.region.slide.diagnoses.all().order_by('name'):
                dx_str += str(dx) + ", "

            outputRow = [ct.cell.id, ct.cell_type, getCellTypeName(ct), ct.cell.region.id,
                         ct.cell.region.slide.name, dx_str, request.user.username]
            writer.writerow(outputRow)
            # print(outputRow)
            # counter += 1
            # if (counter > 500):
            #     break

    return JsonResponse({'success': True})


def export_csv_user_slides(user, slides, export_path):
    # If we later want to output it as a HttpResponse
    #	https://stackoverflow.com/questions/29672477/django-export-current-queryset-to-csv-by-button-click-in-browser
    cells = Cell.objects.filter(region__slide__in=slides.all())
    cellTypes = CellType.objects.filter(user=user, cell__in=cells)
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['labeller_username', 'Cell_pk', 'cell_class',
                        'cell_class_long', 'region_pk', 'slide_pk', 'slide_dx', 'slide_dx_abbrev'])
        for ct in cellTypes:
            writer.writerow([user.username, ct.cell.id, ct.cell_type, getCellTypeName(
                ct), ct.cell.region.id, ct.cell.region.slide.id, diagnosis.name, diagnosis.abbreviation])


def export_each_slide_csv_cellTypes_slides(user, slides, export_path):
    cells = Cell.objects.filter(region__slide__in=slides.all())
    cellTypes = CellType.objects.filter(user=user, cell__in=cells)
    ct_names = cellTypes.values('cell_type').distinct()
    distinct_cell_types = CellType.objects.values_list(
        'cell_type', flat=True).distinct().order_by('cell_type')
    with open(export_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['slide_id', 'slide_name', 'diagnoses',
                        'total']+list(distinct_cell_types))

        # for ct_name in distinct_cell_types:

        for slide in slides:
            print("####" + str(slide))
            dx_str = ''
            for dx in slide.diagnoses.all().order_by('name'):
                dx_str += " " + str(dx)
            cells = Cell.objects.filter(region__slide=slide)
            outputRow = [slide.id, slide.name, dx_str, len(cells)]
            for ct_name in distinct_cell_types:
                count = CellType.objects.filter(
                    user=user, cell__in=cells, cell_type=ct_name).count()
                outputRow = outputRow + [count]
                # print (ct_name + ": "+ str(count))
            writer.writerow(outputRow)

    return

    with open(export_path, 'w', newline='') as f:
        # add header
        writer = csv.writer(f)
        for slide in slides:
            cells = Cell.objects.filter(slide=slide)
            # cellTypes = CellType.objects.filter(user=user, cell__in=cells).values('cell_type').distinct().count()

        writer.writerow(['labeller_username', 'Cell_pk', 'cell_class',
                        'cell_class_long', 'region_pk', 'slide_pk', 'slide_dx', 'slide_dx_abbrev'])
        for ct in cellTypes:
            writer.writerow([user.username, ct.cell.id, ct.cell_type, getCellTypeName(
                ct), ct.cell.region.id, ct.cell.region.slide.id, diagnosis.name, diagnosis.abbreviation])


def export_cell_images_flat(cells, export_path, sizes):
    sizes = [48, 64, 96]
    for size in sizes:
        cell_folder = export_path+str(size)+'/'
        os.system('mkdir '+cell_folder)
        counter = 0
        for cell in cells:
            counter += 1
            if (counter > 10):
                break
            cell_path = cell_folder + str(cell.id) + '.jpg'
            export_cell_image(cell, cell_path, size)


def export_cell_images_celltype_folders(cellTypes, export_path, sizes):
    distinct_cell_types = CellType.objects.values_list(
        'cell_type', flat=True).distinct()
    # print(cellTypes.values('cell_type').distinct())
    # print(len(cellTypes.values('cell_type').distinct()))

    for size in sizes:
        cell_folder_outer = export_path+str(size)+'_sorted/'
        os.system('mkdir '+cell_folder_outer)
        for ctlabel in distinct_cell_types:
            cell_folder = cell_folder_outer + ctlabel + '/'
            os.system('mkdir '+cell_folder)

            # counter = 0
            for ct in cellTypes.filter(cell_type=ctlabel):
                # counter += 1
                # if (counter > 10):
                #     break

                cell = ct.cell
                cell_path = cell_folder + str(cell.id) + '.jpg'
                export_cell_image(cell, cell_path, size)


# Currently just exports for normal diagnosis
@login_required
def export_cell_data(request):
    if (request.user.username != 'admin'):
        print('user access denied in export_cell_data')
        return JsonResponse({'success': False})

    export_path = settings.MEDIA_ROOT + '/export/'
    export_path += datetime.now().strftime("%Y%m%d%H%M%S") + '/'
    os.system('mkdir '+export_path)

    diagnosis = Diagnosis.objects.get(abbreviation='nl')
    slides = Slide.objects.filter(diagnoses=diagnosis)
    # export_csv_user_slides(request.user, slides, export_path+'classes.csv')
    export_each_slide_csv_cellTypes_slides(
        request.user, slides, export_path+'slides_with_cellTypes.csv')
    sizes = [48, 64, 96]
    # cells = Cell.objects.filter(region__slide__in=slides.all()) <-- to delete after testing
    cells = Cell.objects.filter(region__slide__in=slides)
    # export_cell_images_flat(cells, export_path, sizes)

    cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    export_cell_images_celltype_folders(cellTypes, export_path, sizes)

    return JsonResponse({'success': True})


@login_required
def regions(request):
    """Show all regions."""
    # regions = Region.objects.order_by('rid')
    user = request.user
    if user.is_authenticated:
        regions = Region.objects.filter(created_by=request.user).order_by('-date_added')

    regions_json = serializers.serialize("json", regions)

    print('regions_json', regions_json)
    context = {'regions': regions, 'regions_json': regions_json}
    return render(request, 'labeller/regions.html', context)


@login_required
def get_cell_feature_form(request):
    print('entering get_cell_feature_form', request)
    GET = request.GET
    cid = GET['cid']
    cell = Cell.objects.get(cid=cid)
    form = CellFeatureForm(instance=cell)
    # context = {'cellForm': cellForm}
    return HttpResponse(form.as_p())


@login_required
def slides(request):
    """Show all regions."""
    # print(request.user.username)


    # if request.user.is_authenticated:
    #     if request.user == Slide.objects.filter(created_by=request.user):
    #         slides = Slide.objects.order_by('sid')
    #     else:
    #         return error_403(request)
    tissues = Slide.TISSUE_CHOICES
    print('tissues', tissues)
    slides = Slide.objects.filter(created_by=request.user).order_by('sid')
    slides_json = serializers.serialize("json", slides)
    if (len(slides) > 0):
        slides_json = serializers.serialize("json", slides)
    else:
        slides_json = 'none'

    context = {'slides': slides, 'slides_json': slides_json,
               'dx_options': Diagnosis.objects.all()}
    return render(request, 'labeller/slides.html', context)


def getAllCellTypesUserRegionHelper(user, region):
    return CellType.objects.filter(cell__region=region, user=user)


def getAllCellTypesUserRegionJSON(user, region):
    #	print('getAllCellTypesUserRegionJSON(user, region)', user, region)
    return serializers.serialize("json", getAllCellTypesUserRegionHelper(user, region))


def getAllCellTypesUserHelper(user):
    return CellType.objects.filter(user=user)


def getAllCellTypesUserJSON(user):
    #	print('getAllCellTypesUserJSON(user)', user)
    return serializers.serialize("json", getAllCellTypesUserHelper(user))


def getAllCellTypesUserSlideHelper(user, slide):
    return CellType.objects.filter(cell__region__slide=slide, user=user)


def getAllCellTypesSlideUserJSON(user, slide):
    #	print('getAllCellTypesSlideUserJSON(user, slide)', user, slide)
    return serializers.serialize("json", getAllCellTypesUserSlideHelper(user, slide))

# Under construction - used for testing bootstrap


@login_required
def bootstrap_test(request):
    return render(request, 'labeller/bootstrap_test.html')

# Under construction - used for testing bootstrap


@login_required
def label_slide_bootstrap(request, slide_id):
    slide = Slide.objects.get(sid=slide_id)
    diagnoses = slide.diagnoses
    regions = slide.region_set.all()
    context = {'slide': slide, 'dx_options': Diagnosis.objects.all()}
    return render(request, 'labeller/label_slide.html', context)


@login_required
def label_slide(request, slide_id):
    print('label_slide', request, slide_id)

    if request.user.is_authenticated:
        if request.user == Slide.objects.get(sid=slide_id).created_by:
            slide = Slide.objects.get(sid=slide_id)
            # slide = Slide.objects.filter(create_by=request.user)
            # regions = Region.objects.filter(created_by=request.user)
            regions = slide.region_set.all()

            diagnoses = slide.diagnoses

            cells = Cell.objects.filter(created_by=request.user, region__slide=slide)
            cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)

            cells_json = serializers.serialize("json", cells)
            celltypes_json = serializers.serialize("json", cellTypes)

        else:
            return error_403(request)


    # slide = Slide.objects.get(sid=slide_id)

    # diagnoses = slide.diagnoses
    #	print('diagnoses', diagnoses)
    # regions = slide.region_set.all()

    # cells = Cell.objects.filter(region__slide=slide)
    # cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    # print(cells)

    # cells_json = serializers.serialize("json", cells)
    # celltypes_json = serializers.serialize("json", cellTypes)

    context = {'slide': slide, 'regions': regions, 'dx_options': Diagnosis.objects.all(
    ), 'cells': cells, 'cells_json': cells_json, 'celltypes_json': celltypes_json}
    return render(request, 'labeller/label_slide.html', context)


def get_all_cells_json(region):
    cells_json = serializers.serialize("json", region.cell_set.all())
#	print(region, cells_json)
    return cells_json


def get_all_cells_json_project(project):
    cells_json = serializers.serialize("json", project.cells_set.all())
    return cells_json


def get_all_celltypes_json_project(project):
    cells_json = serializers.serialize("json", project.cells_set.all())
    return cells_json


@login_required
def change_cell_location(request):
    POST = request.POST
    cid = POST['cid']
    left = float(POST['left'])
    top = float(POST['top'])
    width = float(POST['width'])
    height = float(POST['height'])
    results = change_cell_location_helper(cid, left, top, width, height)
    return JsonResponse(results)


def change_cell_location_helper(cid, left, top, width, height):
    cell = Cell.objects.get(cid=cid)
    region = cell.region
    if ((top < 0) | (top + height > region.height) | (left < 0) | (left + width > region.width)):
        return {'success': False, 'error': 'box outside boundary'}
    else:
        # This should overwrite the old image
        generate_cell_image_with_vips(region, cid, left, top, width, height)
        cell_path = '/cells/' + str(cid) + '.jpg'
        Cell.objects.filter(cid=cid).update(center_x=left + width/2,
                                            center_y=top + height/2, width=width, height=height, image=cell_path)
        cell = Cell.objects.get(cid=cid)
        cell.center_x_slide = cell.center_x + region.x
        cell.center_y_slide = cell.center_y + region.y
        cell.save()
#		cell = Cell.objects.get(cid=cid);
        cell_json = serializers.serialize("json", [cell])
        results = {'success': True, 'cell_json': cell_json}
        return results


@login_required
def generic_ajax_get(request):
    GET = request.GET
    # print(GET)
    if (GET['id_type'] == 'diagnosis_pk'):
        # print('generic_ajax_get')
        diagnosis = Diagnosis.objects.get(id=GET['id_val'])
        slides = Slide.objects.filter(diagnoses=diagnosis)
        if (GET['query_type'] == 'count'):
            cells = Cell.objects.filter(region__slide__in=slides)
            count = CellType.objects.filter(
                user=request.user, cell__in=cells, cell_type=GET['class_label_abb']).count()
            # print(count)
            results = {'success': True, 'count': count,
                       'class_label_name': GET['class_label_name']}
            return JsonResponse(results)
        elif(GET['query_type'] == 'get_cells_interval'):
            # cells = Cell.objects.filter(region__slide__in=slides)
            # cell_types = CellType.objects.filter(
            #     user=request.user, cell__in=cells, cell_type=GET['class_label_abb']).order_by('id')[int(GET['start']):int(GET['finish'])]
            cell_types = CellType.objects.filter(
                user=request.user, cell__region__slide__in=slides, cell_type=GET['class_label_abb']).order_by('id')[int(GET['start']):int(GET['finish'])]
            new_cells = Cell.objects.filter(celltype__in=cell_types)

            # for ct in cell_types:
            #     print(str(ct))

            # for cell in new_cells:
            #     print(cell)
            # print('counts')
            # print('cell_types: ' + str(cell_types.count()))
            # print('new_cells: ' + str(new_cells.count()))
            # print('class_label_name', GET['class_label_name'])

            results = {'success': True, 'cell_types_json': serializers.serialize("json", cell_types),
                       'cells_json': serializers.serialize("json", new_cells),
                       'class_label_name': GET['class_label_name'],
                       'start': GET['start'], 'finish': GET['finish'],
                       'class_label_abb': GET['class_label_abb']}
            return JsonResponse(results)

        elif(GET['query_type'] == 'all_cells_single_type'):
            cell_types = CellType.objects.filter(
                user=request.user, cell__region__slide__in=slides, cell_type=GET['class_label_abb']).order_by('id')
            print('cell_types', cell_types)
            new_cells = Cell.objects.filter(celltype__in=cell_types)
            print('new_cells', new_cells)
            results = {'success': True, 'cell_types_json': serializers.serialize("json", cell_types),
                       'cells_json': serializers.serialize("json", new_cells),
                       #    'class_label_name': GET['class_label_name'],
                       'class_label_abb': GET['class_label_abb']}
            return JsonResponse(results)

        elif(GET['query_type'] == 'more_cells_single_type'):
            print('more_cells_single_type')
            print(GET['old_finish'])
            print(GET['num_new_cells'])
            old_finish = int(GET['old_finish'])
            new_finish = old_finish+int(GET['num_new_cells'])
            # if (new_finish > CellType.objects.filter(
            #     user=request.user, cell__in=cells, cell_type=GET['class_label_abb']).count()){

            # }
            cell_types = CellType.objects.filter(
                user=request.user, cell__region__slide__in=slides, cell_type=GET['class_label_abb']).order_by('id')[old_finish:new_finish]
            new_cells = Cell.objects.filter(celltype__in=cell_types)
            results = {'success': True, 'cell_types_json': serializers.serialize("json", cell_types),
                       'cells_json': serializers.serialize("json", new_cells),
                       #    'class_label_name': GET['class_label_name'],
                       'class_label_abb': GET['class_label_abb'],
                       'new_finish': new_finish}
            return JsonResponse(results)

        # elif(GET['query_type'] == 'get_cell'):
        #     cells = Cell.objects.filter(region__slide__in=slides)
        #     cell_types = CellType.objects.filter(
        #         user=request.user, cell__in=cells, cell_type=GET['class_label_abb']).order_by('id')[int(GET['start']):int(GET['finish'])]
        #     results = {'success': True, 'cell_types': serializers.serialize("json", cell_types),
        #                'class_label_name': GET['class_label_name']}
        #     return JsonResponse(results)

        # results = get_all_cells_generic_helper(
        #     request, 'diagnosis_pk', GET['query_parent_id'])
        # print(results)
    # project_id = GET['project_id']
    # print(project_id)
    # project = Project.objects.get(id=project_id)
    # cells_json = serializers.serialize("json", project.cell_set.all())
    results = {'success': True}
    # results = {'success': True, 'cells_json': cells_json,
    #            'celltypes_json': getAllCellTypesUserJSON(request.user)}
    return JsonResponse(results)

# Used by slide_summary.html


@ login_required
def get_all_cells_generic(request):
    GET = request.GET
    id_type = GET['id_type']
    id_val = GET['id_val']
    print(id_type, id_val)
    results = get_all_cells_generic_helper(request, id_type, id_val)
    return JsonResponse(results)

# Used by slide_summary.html


@ login_required
def get_all_cells_generic_helper(request, id_type, id_val):
    # GET = request.GET
    # id_type = GET['id_type']
    # id_val = GET['id_val']
    print(id_type, id_val)
    if (id_type == 'sid'):
        cells = Cell.objects.filter(region__slide__sid=id_val)
        cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
        # celltypes_json = getAllCellTypesSlideUserJSON(request.user, Slide.objects.get(sid=id_val))
    elif (id_type == 'rid'):
        cells = Cell.objects.filter(region__rid=id_val)
        cellTypes = CellType.objects.filter(
            cell__region=id_val, user=request.user)
        # celltypes_json = getAllCellTypesUserRegionJSON(request.user, Region.objects.get(rid=id_val))
    elif (id_type == 'project_pk'):
        project = Project.objects.get(id=id_val)
        slides = Slide.objects.filter(slides_with_project=project)
        cells = Cell.objects.filter(region__slide__in=slides)
        cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    elif (id_type == 'diagnosis_pk'):
        diagnosis = Diagnosis.objects.get(id=id_val)
        slides = Slide.objects.filter(diagnoses=diagnosis, created_by=request.user)
        cells = Cell.objects.filter(region__slide__in=slides)
        cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
        print('diagnosis', diagnosis)
        print('slides', slides)
        print('cells', cells)
        print('cellTypes', cellTypes)
    else:
        results = {'success': False}
        return results

    results = {'success': True, 'cells_json': serializers.serialize(
        "json", cells), 'celltypes_json': serializers.serialize("json", cellTypes)}
    print('results', results)
    # print('get all cells generic results', results['cells_json'])
    return results

# Used by CellCounter.js


@ login_required
def get_all_cells_in_region(request):
    #	print("get_all_cells_in_region", request)
    GET = request.GET
    rid = GET['rid']
    region = Region.objects.get(rid=rid)
    print(region)

    cells_json = serializers.serialize("json", region.cell_set.all())
    results = {'success': True, 'cells_json': cells_json,
               'celltypes_json': getAllCellTypesUserRegionJSON(request.user, region)}
    return JsonResponse(results)

# Used by slides.html


@ login_required
def get_all_cells_in_slide(request):
    print('get_all_cells_in_slide(request)', request)
    GET = request.GET
    sid = GET['sid']
    cells = Cell.objects.filter(region__slide__sid=sid)
    print('length of cells', len(cells))
    slide = Slide.objects.get(sid=sid)
    cells_json = serializers.serialize("json", cells)
    results = {'success': True, 'cells_json': cells_json,
               'celltypes_json': getAllCellTypesSlideUserJSON(request.user, slide)}
    print('exiting get_all_cells_in_slide')
    return JsonResponse(results)

# Currently only used by returnObjectToOlDCoordinates(canvas, obj) in Cell.js, which is why celltype is not sent


@ login_required
def get_cell_json(request):
    GET = request.GET
    cid = GET['cid']
    cell = Cell.objects.get(cid=cid)
    cell_json = serializers.serialize("json", [cell])
    results = {'success': True, 'cell_json': cell_json}
    return JsonResponse(results)


# vips crop
# extract an area from an image
# usage:
#    extract_area input out left top width height [--option-name option-value ...]
# where:
#    input        - Input image, input VipsImage
#    out          - Output image, output VipsImage
#    left         - Left edge of extract area, input gint
# 			default: 0
# 			min: -10000000, max: 10000000
#    top          - Top edge of extract area, input gint
# 			default: 0
# 			min: -10000000, max: 10000000
#    width        - Width of extract area, input gint
# 			default: 1
# 			min: 1, max: 10000000
#    height       - Height of extract area, input gint
# 			default: 1
# 			min: 1, max: 10000000


# need to make sure CIDs do not start with trailing 0s as this causes problems

def create_new_cid():
    now = datetime.now()
    date_time = now.strftime("%m%d%Y%H%M%S")
    return "1"+date_time


def create_new_cell(rid, left, top, width, height, user):
    left = int(left)
    top = int(top)
    width = int(width)
    height = int(height)
    print(rid, left, top, width, height)
    print(type(rid), type(left), type(top), type(width), type(height))
    region = Region.objects.get(rid=rid)
    if ((top < 0) | (top + height > region.height) | (left < 0) | (left + width > region.width)):
        return {'success': False, 'error': 'box outside boundary'}

    else:
        # region = Region.objects.get(rid=rid)
        cid = create_new_cid()
        generate_cell_image_with_vips(region, cid, left, top, width, height)
        cell_path = '/cells/' + cid + '.jpg'

        new_cell = Cell.objects.create(created_by=user, region=region, image=cell_path, cid=cid,
                                       center_x=left + width/2, center_y=top + height/2, width=width, height=height)
        new_cell.center_x_slide = new_cell.center_x + region.x
        new_cell.center_y_slide = new_cell.center_y + region.y
        new_cell.save()
        new_cell_type = CellType.objects.create(cell=new_cell, user=user)

        new_cell_json = serializers.serialize("json", [new_cell])
        new_cell_type_json = serializers.serialize("json", [new_cell_type])
        results = {'success': True, 'new_cell_json': new_cell_json}
        return results


@ login_required
def add_new_cell_box(request):
    POST = request.POST
    rid = int(POST['rid'])

    top = float(POST['top'])
    height = float(POST['height'])

    left = float(POST['left'])
    width = float(POST['width'])

    # Note: the return for create_new_cell is:
    # results = {'success':True, 'new_cell_json':new_cell_json, 'cells_json':cells_json, 'new_cell_type_json': new_cell_type_json, 'celltypes_json': all_cell_types_json, 'celltypes': celltypes_in_region}
    results = create_new_cell(rid, left, top, width, height, request.user)

    return JsonResponse(results)


@ login_required
def toggle_region_complete_class(request):
    POST = request.POST
    rid = int(POST['rid'])
    if (POST['value'] == 'true'):
        value = True
    else:
        value = False
    # print('toggle_region_complete_seg', POST['value'], value)
    success = Region.objects.filter(rid=rid).update(all_wc_classified=value)
    results = {'success': (success == 1)}
    return JsonResponse(results)


@ login_required
def toggle_region_complete_seg(request):
    POST = request.POST
    rid = int(POST['rid'])
    if (POST['value'] == 'true'):
        value = True
    else:
        value = False
    # print('toggle_region_complete_seg', POST['value'], value)
    success = Region.objects.filter(rid=rid).update(all_wc_located=value)
    results = {'success': (success == 1)}
    return JsonResponse(results)


@ login_required
def add_diagnosis_to_slide(request):
    try:
        POST = request.POST
        print(POST)
        diagnosis = Diagnosis.objects.get(id=POST['diagnosis_pk'])
        slide = Slide.objects.get(id=POST['slide_pk'])
        slide.diagnoses.add(diagnosis)
        slide.save()
        print(slide, slide.diagnoses)
        print('success')
        return JsonResponse({'success': True})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False})


def remove_diagnosis_from_slide(request):
    try:
        POST = request.POST
        diagnosis = Diagnosis.objects.get(id=POST['diagnosis_pk'])
        slide = Slide.objects.get(id=POST['slide_pk'])
        slide.diagnoses.remove(diagnosis)
        slide.save()
        return JsonResponse({'success': True})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False})

# Function to add Notes to Slide + Region
@login_required
@csrf_exempt
def add_note_to_slide(request):
    id = request.POST.get('slide_sid')
    print(id)
    type = request.POST.get('type')
    print(type)
    value = request.POST.get('value')
    print(value)
    slide = Slide.objects.get(sid=id)
    print(slide)
    slide.notes = value

    slide.save()

    return JsonResponse({'success': "slide note updated"})

@login_required
@csrf_exempt
def add_tissue_type_to_slide(request):
    id = request.POST.get('slide_sid')
    print(id)
    key = request.POST.get('key')
    print(key)
    slide = Slide.objects.get(sid=id)
    print(slide)

    slide.tissue = key

    print(slide.tissue)

    slide.save()

    return JsonResponse({'success': "slide tissue updated"})







# @login_required
# def add_note_to_slide(request):
#     try:
#         POST = request.POST
#         print('CANNONBALL RUN!')
#         # print(POST)
#         note = Slide.objects.get(id=POST['slide.sid']).value()
#         # print(note)
#         slide = Slide.objects.get(id=POST['slide.sid'])
#         slide.notes.add(note)
#         slide.save()
#         # print(slide, slide.notes)
#         # print('success')
#         return JsonResponse({'success': True})

#     except Exception as e:
#         # print(e)
#         print('fail')

#         return JsonResponse({'success': False})


# @login_required
# def add_new_cell(request):
# 	POST = request.POST
# 	rid = POST['rid']
# 	center_x = float(POST['center_x'])
# 	center_y = float(POST['center_y'])
# 	box_dim = 90 # Box dimension (it is a square)
# 	left = center_x - box_dim/2
# 	top = center_y - box_dim/2
# 	return JsonResponse(create_new_cell(rid, left, top, box_dim, box_dim, request.user))


@ login_required
def delete_region(request):

    user = request.user
    rid = request.POST['rid']

    if user.is_authenticated:
        if user.id == Region.objects.filter(rid=rid, created_by=user):
            print(Region.objects.filter(rid=rid, created_by=user))
            region = Region.objects.filter(rid=rid, created_by=user)
            region.delete()

    print('deleting region %s' % rid)
    # region = Region.objects.filter(rid=rid).delete()
    results = {'success': True}
    return JsonResponse(results)

# Needs updating with celltypes


@ login_required
def delete_cell(request):
    POST = request.POST
    cid = POST['cid']
    print('deleting cell %s' % cid)
    cell = Cell.objects.filter(cid=cid).delete()
    print('deleting', cell)
    results = {'success': True}
    return JsonResponse(results)


@ login_required
def add_new_region(request):
    POST = request.POST
    sid = POST['sid']
    x1 = float(POST['x1'])
    y1 = float(POST['y1'])
    x2 = float(POST['x2'])
    y2 = float(POST['y2'])

    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x1-x2)
    height = abs(y1-y2)

    slide = Slide.objects.get(sid=sid)
    svs_path = settings.MEDIA_ROOT + slide.svs_path.url
    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M%S")
    region_path = settings.MEDIA_ROOT + '/regions/' + date_time + '.jpg'
    command = "vips crop " + svs_path + " " + region_path + " " + str(x) + " " + str(y) + " " + \
        str(width) + " " + str(height)
    print(command)
    os.system(command)
#	image =	image_model.image_field(region_path, File().read())

    region_path = '/regions/' + date_time + '.jpg'
    new_region = Region.objects.create(created_by=request.user, slide=slide,
                                       image=region_path, rid=date_time, x=x, y=y, width=width, height=height)
    new_region.save()
#	new_region.image.save(os.path.basename(.url))

#	new_region.image.url = region_path

#	file = open(region_path)
#	myfile = File(f)
#	new_region.image.
# print(MEDIA_ROOT)

    results = {'success': True, 'rid': date_time, 'region_path': region_path}
    return JsonResponse(results)


def add_additional_cellType_to_cell(request):
    POST = request.POST
    # request.user, Cell.objects.get(cid=POST['cid']), POST['cell_label']


# Will attempt to assign a new cellType. If one does not exist, it will be created.
def update_cellType_helper(user, cell, cell_type):
    try:
        print("changing cellType")
        cellType = CellType.objects.get(user=user, cell=cell)
        cellType.cell_type = cell_type
        cellType.save()
        print(cellType)
    except CellType.DoesNotExist:
        print("did not exist")
        cellType = CellType.objects.create(
            user=user, cell_type=cell_type, cell=cell)
    return cellType

# Will attempt to assign a new cellType. If one does not exist, it will be created.


def get_cellType_helper(user, cell):
    try:
        print("getting cellType")
        cellType = CellType.objects.get(user=user, cell=cell)
        print(cellType)
    except CellType.DoesNotExist:
        print("did not exist. creating one")
        CellType.objects.create(user=user, cell=cell)
    return cellType


def getCellTypeNameFromStringCode(cell_type_code):
    classLabelDict = {
        "M1": "Blast",
        "M2": "Promyelocyte",
        "M3": "Myelocyte",
        "M4": "Metamyelocyte",
        "M5": "Band neutrophil",
        "M6": "Segmented netrophil",

        "E1": "Immature Eosinophil",
        "E2": "Mature Eosinophil",
        "B1": "Mast Cell",
        "B2": "Basophil",
        "MO1": "Monoblast",
        "MO2": "Monocyte",

        "L0": "Lymphoblast",
        "L1": "Hematogone",
        "L2": "Small Mature Lymphocyte",
        "L3": "Reactive lymphocyte/LGL",
        "L4": "Plasma Cell",

        "ER1": "Pronormoblast",
        "ER2": "Basophilic Normoblast",
        "ER3": "Polychromatophilic Normoblast",
        "ER4": "Orthochromic Normoblast",
        "ER5": "Polychromatophilic Erythrocyte",
        "ER6": "Mature Erythrocyte",

        "U1": "Artifact",
        "U2": "Unknown",
        "U3": "Other",
        "U4": "Mitotic Body/karyorrhexis",
        "UL": "Unlabelled",

        "PL1": "Immature Megakaryocyte",
        "PL2": "Mature Megakaryocyte",
        "PL3": "Platelet Clump",
        "PL4": "Giant Platelet",
    }

    return classLabelDict[cell_type_code]


def getCellTypeName(cellType):
    return getCellTypeNameFromStringCode(cellType.cell_type)


@ login_required
def update_cell_class(request):
    #	user = request.user
    POST = request.POST
    # cell = Cell.objects.get(cid=POST['cid'])
    # cell.cell_type = POST['cell_label']
    # cell.save()
    cellType = update_cellType_helper(
        request.user, Cell.objects.get(cid=POST['cid']), POST['cell_label'])

    print('update_cell_class(request) Cell class CID:' +
          str(POST['cid'])+' new_class: '+cellType.cell_type + " - " + getCellTypeName(cellType))
    results = {'success': True}
    return JsonResponse(results)


@ login_required
# def update_cell_class_in_project(request):
#     POST = request.POST
#     # cell = Cell.objects.get(cid=POST['cid'])
#     # cell.cell_type = POST['cell_label']
#     # cell.save()
#     update_cellType_helper(request.user, Cell.objects.get(
#         cid=POST['cid']), POST['cell_label'])
#     results = {'success': True,
#                'cells_json': get_all_cells_json_project(cell.project)}
#     return JsonResponse(results)
@ login_required
def data_export(request):
    regions = Region.objects.all()
    regions_json = serializers.serialize("json", Region.objects.all())
    cells = Cell.objects.all()
    cells_json = serializers.serialize("json", Cell.objects.all())

    context = {'regions': regions, 'regions_json': regions_json,
               'cells': cells, 'cells_json': cells_json}
    return render(request, 'labeller/data_export.html', context)


@ login_required
def stats(request):
    regions = Region.objects.all()
    regions_json = serializers.serialize("json", Region.objects.all())
    cells = Cell.objects.all()
    cells_json = serializers.serialize("json", Cell.objects.all())

    context = {'regions': regions, 'regions_json': regions_json, 'cells': cells,
               'cells_json': cells_json, 'celltypes_json': getAllCellTypesUserJSON(request.user)}
    return render(request, 'labeller/stats.html', context)


@ login_required
def cell_redirect(request, cell_pk):
    cell = Cell.objects.get(id=cell_pk)
    # return label_region_fabric(request, cell.region.rid)
#	return redirect('/label_region_fabric/'+str(cell.region.rid))
    return HttpResponseRedirect('/label_region_fabric/'+str(cell.region.rid)+'/')


@ login_required
def label_region_fabric(request, region_id):
    print('Entering label_region_fabric', request.user)
    if (request.user.username == 'admin'):
        print('\thello user admin')
        # cells = Cell.objects.all()
        # print("# cells = ", len(cells))
        # print("# celltypes admin", len(CellType.objects.filter(user=request.user)))
        # print("# celltypes all", len(CellType.objects.all()))
        # for objx in Project.objects.all():
        # 	print(objx, 'created_by:', objx.created_by)
        # 	objx.created_by = User.objects.get(username='admin')
        # 	objx.save()

    # for cell in cells:
    # 	update_cellType_helper(request.user, cell, cell.cell_type)

    """label cells on a region"""
    print("THIS IS THE  SPINALTAP")
    if request.user.is_authenticated:
        if request.user == Region.objects.get(rid=region_id).created_by:
            region = Region.objects.get(rid=region_id)
        else:
            return error_403(request)

    region = Region.objects.get(rid=region_id)
    slide = region.slide
    cells = region.cell_set.all()
    if (cells.count() == 0):
        # cells = "none"
        cells_json = "none"
    else:
        cells_json = serializers.serialize("json", region.cell_set.all())

    celltypes_in_region = getAllCellTypesUserRegionJSON(request.user, region)
    context = {'region': region, 'cells': cells, 'dx_options': Diagnosis.objects.all(
    ), 'cells_json': cells_json, 'slide': slide, 'celltypes_json': celltypes_in_region}
    # print('label_region_fabric context', context)
    return render(request, 'labeller/label_region_fabric.html', context)


@ login_required
def get_all_cells_in_project(request):
    GET = request.GET
    project_id = GET['project_id']
    print(project_id)
    project = Project.objects.get(id=project_id)
    cells_json = serializers.serialize("json", project.cell_set.all())
    results = {'success': True, 'cells_json': cells_json,
               'celltypes_json': getAllCellTypesUserJSON(request.user)}
    return JsonResponse(results)


# UserForm view
def register(request):

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.info(
                request, "Thank you for registering. You are now logged in.")
            new_user = authenticate(
                username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, new_user)
            return HttpResponseRedirect('/')
        else:
            print('form not valid')
            print(form)

    else:
        form = UserForm()

    return render(request, 'labeller/register.html', {'form': form})


# Not currenlty in use
@ login_required
def get_number_of_slides_with_diagnosis_name(request):
    GET = request.GET
    diagnosis_name = GET['diagnosis_name']
    print(diagnosis_name)

    diagnosis_count = 0
    for slide in Slide.objects.all():
        for diagnosis in slide.diagnoses.all():
            if diagnosis.name == diagnosis_name:
                diagnosis_count += 1

    results = {'success': True, 'diagnosis_count': diagnosis_count}
    return JsonResponse(results)


def calculate_slide_diagnosis_counts(slides, diagnoses):
    diagnosis_counts = {}
    for diagnosis in diagnoses:
        diagnosis_counts[diagnosis.name] = 0

    slides = Slide.objects.all()
    for slide in slides:
        for diagnosis in slide.diagnoses.all():
            diagnosis_counts[diagnosis.name] += 1

    print(diagnosis_counts)
    return diagnosis_counts

# Diagnoses page view


@ login_required
def diagnoses(request):
    """Show all projects"""
    # user_projects = Project.objects.filter(user=request.user.get_username()).order_by('id')
    # context = {'user_projects': user_projects}
    diagnoses = Diagnosis.objects.all()

    diagnosis_counts = calculate_slide_diagnosis_counts(
        Slide.objects.all(), diagnoses)
    serializers.serialize

    context = {'diagnoses': diagnoses,
               'diagnosis_counts_json': json.dumps(diagnosis_counts),
               #    'diagnosis_counts': diagnosis_counts
               }

    return render(request, 'labeller/diagnoses.html', context)


# Projects page view
@ login_required
def projects(request):
    """Show all projects"""
    # user_projects = Project.objects.filter(user=request.user.get_username()).order_by('id')
    # context = {'user_projects': user_projects}

    projects = Project.objects.filter(created_by=request.user).order_by('id')
    context = {'projects': projects}
    print(Project.id)

    return render(request, 'labeller/projects.html', context)

    # def get_queryset(self):
    # user = self.request.user
    # return Project.objects.filter(user)


@ login_required
def create_project(request):
    if request.method == 'POST':
        if request.POST.get('project') != None:
            proj = request.POST.get('project')
            project = Project.objects.create(
                name=proj, created_by=request.user)
            print(proj)
            print(project)

        else:
            return render(request, 'labeller/projects.html')

            # context = {'project': project}

    # return HttpResponseRedirect(reverse('labeller:label_cells_in_project'))
    return render(request, 'labeller/label_cells_in_project.html')


# Needs updating with celltypes
@ login_required
def export_project_data(request):
    GET = request.GET
    project_id = GET['project_id']
    print(request, project_id)
    project = Project.objects.get(id=project_id)
    all_cells = project.cell_set.all()
    list_of_cell_dicts = []
    for cell in all_cells:
        print(cell)
        list_of_cell_dicts.append(cell.asdict())
    print(list_of_cell_dicts)
    df = pd.DataFrame(list_of_cell_dicts)
    print(df)

    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M%S")
    filename = project_id + '_' + date_time + '.xlsx'
    df.to_excel(DATA_EXPORT_ROOT + '/' + filename, index=False)

    results = {'success': True, 'filename': '/data_export/' + filename}
    return JsonResponse(results)


def create_slide_pyramid_with_vips(sid):
    print("entering create_slide_pyramid_with_vips", sid)
    slide_svs = '/slides/' + sid + '.svs '
    command = "vips dzsave " + settings.MEDIA_ROOT + slide_svs + \
        settings.MEDIA_ROOT + '/slides/' + sid
    print('command', command)
    os.system(command)
    print('done')
    return('slides/' + sid + '.dzi')

    # pyvips for django lib for saving file in dz
    # image = pyvips.Image.new_from_file("myslide.svs", associated="thumbnail")
    # image.dzsave("something")


def generate_cell_image_with_vips(region, cid, left, top, width, height):
    cid = str(cid)
    region_path = settings.MEDIA_ROOT + region.image.url
    cell_path = settings.MEDIA_ROOT + '/cells/' + cid + '.jpg'
    command = "vips crop " + region_path + " " + cell_path + " " + \
        str(left) + " " + str(top) + " " + \
        str(width) + " " + str(height)
    os.system(command)

# Upload handler for dzi WSIs and also Excel files relating to them


@ login_required
def dropzone_slide(request):
    print('entering dropzone_slide')
    if request.method == "POST":
        i = 0

        slide_list = []

        for image in request.FILES.getlist('file'):
            print(image)
            extension = image.name[-4:]
            print(extension)

            if extension == ".svs":
                sid = create_new_cid()+str(i)
                i += 1
                print(i)
                name = image.name
                image.name = str(sid) + '.svs'
                slide = Slide.objects.create(created_by=request.user, sid=sid, date_added=str(
                    datetime.now()), name=name, svs_path=image)

                if (name[:4] == 'nlbx'):
                    print('normal slide')
                    diagnosis = Diagnosis.objects.get(id=1)
                    print(diagnosis)
                    slide.diagnoses.add(diagnosis)

                print(slide)
                # print(slide.sid)
                # print(slide.name)
                # print(slide.date_added)
                # print(id)
                slide.dzi_path = create_slide_pyramid_with_vips(sid)
                # print(slide.dzi_path)
                slide.save()
                slide_list.append(slide)
        slides_json = serializers.serialize("json", slide_list)
        print(slides_json)
        results = {'success': True, 'slides_json': slides_json}
        return JsonResponse(results)

    # return HttpResponse()

    # Check if it is a .dzi file or a .xlsx file
    # If .dzi files

        # Create new slide object
        # Save slide object
        # get slide sid
        # create_slide_pyramid_with_vips(sid)
    # If .xlsx
        # Do something else to be written
    return


@ login_required
def dropzone_image_w_projectID(request, project_id):
    print("entering dropzone_image_w_projectID")
    if request.method == "POST":
        print(request)
        print(request.FILES)
        print(request.FILES.getlist('file'))
        i = 0
        # proj = request.POST.get('project')
        # project_id = Project.name
        project = Project.objects.get(id=project_id)
        cell_list = []
        for image in request.FILES.getlist('file'):
            print(image)
            print(type(image))
            cid = int(create_new_cid()+str(i))
            i += 1
            name = image.name
            cell_type = request.POST.get('cell_type')
            cells_json = serializers.serialize("json", project.cell_set.all())

            # project = request.POST.get('project')
            # print(proj)
            print(cell_type)
            print(project)
            print(project_id)
            print(name)
            print(image)
            print(cid)
            print(cells_json)
            cell = Cell.objects.create(created_by=request.user, image=image, cid=cid,
                                       name=name, project=project, project_id=project_id, cell_type=cell_type)
            new_cell_type = CellType.objects.create(
                cell=cell, user=request.user)
            cell.save()
            update_cellType_helper(request.user, cell, cell_type)
            cell_list.append(cell)
        cells_json = serializers.serialize("json", cell_list)
        print('cell list: ' + str(cell_list))
        print('cells json: ' + str(cells_json))
        results = {'success': True,  'cells_json': cells_json, }
        return JsonResponse(results)
        # return HttpResponse()

    return HttpResponse()


@ login_required
def all_cells_for_diagnosis(request, diagnosis_id):
    diagnosis = Diagnosis.objects.get(id=diagnosis_id)

    user = request.user
    if user.is_authenticated:
        slides = Slide.objects.filter(diagnoses=diagnosis, created_by=user)
        cells = Cell.objects.filter(region__slide__in=slides.all())
        cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
        cells_json = serializers.serialize("json", cells)
        celltypes_json = serializers.serialize("json", cellTypes)


    # slides = Slide.objects.filter(diagnoses=diagnosis)
    # cells = Cell.objects.filter(region__slide__in=slides.all())
    # cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    # cells_json = serializers.serialize("json", cells)
    # celltypes_json = serializers.serialize("json", cellTypes)
    context = {'diagnosis': diagnosis, 'cells': cells,
               'cells_json': cells_json, 'celltypes_json': celltypes_json}
    return render(request, 'labeller/all_cells_for_diagnosis.html', context)


@ login_required
def all_cells_for_diagnosis2(request, diagnosis_id):
    diagnosis = Diagnosis.objects.get(id=diagnosis_id)
    # slides = Slide.objects.filter(diagnoses=diagnosis)
    # cells = Cell.objects.filter(region__slide__in=slides.all())
    # cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    # cells_json = serializers.serialize("json", cells)
    # celltypes_json = serializers.serialize("json", cellTypes)
    context = {'diagnosis': diagnosis}
    # context = {'diagnosis': diagnosis, 'cells': cells,
    #            'cells_json': cells_json, 'celltypes_json': celltypes_json}

    return render(request, 'labeller/all_cells_for_diagnosis2.html', context)


@ login_required
def diagnosis(request, diagnosis_id):
    diagnosis = Diagnosis.objects.get(id=diagnosis_id)

    # https://www.sankalpjonna.com/learn-django/the-right-way-to-use-a-manytomanyfield-in-django
    # slides = Slide.objects.filter(diagnoses=diagnosis)

    user = request.user
    if user.is_authenticated:
        slides = Slide.objects.filter(diagnoses=diagnosis, created_by=user)
        # diagnosis = diagnosis.slides_with_diagnosis.all()
        print(diagnosis)

    # for slide in slides:
    # 	print(slide, Cell.objects.filter(region__slide=slide))
    # print(slides)

    # cells = Cell.objects.filter(region__slide__in=slides.all())
    # cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)
    # cells_json = serializers.serialize("json", cells)
    # celltypes_json = serializers.serialize("json", cellTypes)
    # context = {'diagnosis': diagnosis, 'slides': slides, 'cells': cells,
    #            'cells_json': cells_json, 'celltypes_json': celltypes_json,  'dx_options': Diagnosis.objects.all()}

    context = {'diagnosis': diagnosis, 'slides': slides,
               'dx_options': Diagnosis.objects.all()}

    return render(request, 'labeller/diagnosis.html', context)


@ login_required
def project(request, project_id):
    project = Project.objects.get(id=project_id)
    # slides = Slide.objects.filter(project_with_slides=project)
    cells = Cell.objects.filter(region__slide__in=project.slides.all())
    regions = Region.objects.filter(slide__in=project.slides.all())
    cellTypes = CellType.objects.filter(user=request.user, cell__in=cells)

    cells_json = serializers.serialize("json", cells)
    celltypes_json = serializers.serialize("json", cellTypes)

    context = {'project': project, 'regions': regions, 'cells': cells,
               'cells_json': cells_json, 'celltypes_json': celltypes_json}
    return render(request, 'labeller/project.html', context)

# Not currently in use - may require fixing


@ login_required
def label_cells_in_project(request, project_id):
    """label cells in a given project"""
    print(project_id)
    project = Project.objects.get(id=project_id)
    print(project)
    cells = project.cell_set.all()
    name = project.name

    if (cells.count() == 0):
        cells = "none"
        cells_json = "none"
    else:
        cells_json = serializers.serialize("json", project.cell_set.all())

    context = {'project': project, 'name': name, 'cells': cells,
               'cells_json': cells_json, 'celltypes_json': getAllCellTypesUserJSON(request.user)}
    print(context)

    return render(request, 'labeller/label_cells_in_project.html', context)


# CUSTOM ERROR PAGES - WILL NEED SOME WORK. IE NOT SURE WHAT ERROR CODES TO USE, ETC....
def error_403(request):
    return render(request, 'errormsgs/error_403.html')

# def update_cell_class(request):
# 	results = {'success':False}
# 	if request.method == 'GET':
# 		GET = request.GET
# 		if 'cid' in GET and 'cell_label' in GET:
# 			cid = int(GET['cid'])
# 			cell_label = GET['cell_label']
# 			cell = Cell.objects.get(cid=cid)
# 			form = CellLabelFormChoices(request.POST, instance=cell)

# 			form.save(update_fields['cell_label', cell_label])
# 			results = {'success': True}
# 	json_response = json.dumps(results)
# 	return HttpResponse(json_response)


# def update_cell_class(request, cell_id):
    # if request.method=='POST': and request.is_ajax():
    # 	try:
    # 		cell = Cell.objects.get(id=cell_id)
    # 		cell.cell_label = request.POST['cell_label']
    # 		cell.save()
    # 		return JsonResponse({'status':'Success', 'msg':'save successfully'})
    # 	except Cell.DoesNotExist:
    # 		return JsonResponse({'status':'Fail', 'msg':'Not a valid request'})


# def region_images(request):
# 	"""show all region images"""
# 	region_images = Region.image.order_by('rid')
# 	context = {'region_images': region_images}
# 	return render(request, 'labeller/regions.html, context')

# Needs updating with celltypes
# @login_required
# def cells(request):
# 	"""Show all regions."""
# 	cells = Cell.objects.order_by('cid')
# 	cells_json = serializers.serialize("json", cells)
# 	cell_forms_dict = {}
# 	cell_forms_array = []
# 	for cell in cells:
# 		cell_forms_dict[cell.cid] = CellFeatureForm(instance=cell)
# 		cell_forms_array.append(CellFeatureForm(instance=cell))

# 	context = {'cells': cells, 'cells_json': cells_json, 'cell_forms_dict': cell_forms_dict, 'cell_forms_array': cell_forms_array, 'celltypes_json': getAllCellTypesUserJSON(request.user) }
# 	return render(request, 'labeller/cells.html', context)


# class AddCellFeatures(CreateView):
# 	model = Cell
# 	form_class = CreateMyeloidForm
# 	template_name = '/cells/addCellFeatures.html'
# 	success_url = reverse_lazy('index')

# def export_project_data(request):
# 	projects = Project.objects.filter('id')
# 	with open(r'.\\labeller\\{{ project_id }}.json', "w") as out:
# 		mast_point = serializers.serialize("json", projects)
# 		out.write(mast_point)
# 	template = __loader__.get_template('')
# 	project = Project.objects.get('id')
# 	cells_json = serializers.serialize("json", Cell.objects.filter(project.id))
# 	context = {'project': project, 'cells_json': cells_json}

# 	return render(request, 'labeller/data_export.html', context)

# def export_project_data(target_path, target_file, data):
#   data = serializers.serialize("json", Project.objects.GET('id'))
#   print(data)

#   if not os.path.exists(target_path):
#     try:
#       os.makedirs(target_path)
#     except Exception as e:
#       print(e)
#       raise
#   with open(os.path.join(target_path, target_file), 'w') as f:
#     json.dump(data, f)

#   file = export_project_data('/hemelabel/', 'project_data.json', data)
#   print(file)
#   return file

# def export_project_data(request, project_id):


# Needs to be udpated to support changing slide and patient as well
# @login_required
# def next_region(request):
# 	POST = request.POST
# 	rid = POST['rid']
# 	direction = int(POST['direction'])
# 	region = Region.objects.get(rid=rid)
# 	results = {'rid': rid, 'success':False}

# 	print(direction)
# 	print(rid)
# 	print(region)
# 	print(region.slide)
# 	# #regions = Region.objects.filter(slide=region.slide)

# 	if (direction == 1):
# 		next_region = Region.objects.filter(slide=region.slide, rid__gt=rid).order_by('rid').first()
# 	elif (direction == -1):
# 		next_region = Region.objects.filter(slide=region.slide, rid__lt=rid).order_by('rid').last()

# 	if (next_region != None):
# 		results = {'rid': next_region.rid, 'success':True}

# 	# else :
# 	# 	print(next_region)

# 	return JsonResponse(results)

# @login_required
# def cells2(request):
# 	slide_array = []
# 	slides = Slide.objects.order_by('date_added')
# 	for slide in slides:
# 		slide_regions = Region.objects.filter(slide=slide)
# 		region_list = []
# 		for region in slide_regions:
# 			cell_tuple_array = []
# 			cells = Cell.objects.filter(region=region)
# 			for cell in cells:
# 				# Append tuple-array of cells and cellfeautureforms and add to array
# 				cell_tuple_array.append([cell, CellFeatureForm(instance=cell)])
# 			#Append tuple-array of region with lists of {cell, cell form} tuples
# 			region_list.append([region, cell_tuple_array])
# 		#Append tuple-array of slide with region list tuples
# 		slide_array.append([slide, region_list])
# 	print(slide_array)
# 	context = {'slide_list': slide_array}

# 	return render(request, 'labeller/cells2.html', context)


# @login_required
# def get_cellType(request):
# 	GET = request.GET
# 	id = GET['id']
# 	cell = Cell.objects.get(id=id)
# 	cellType = get_cellType_helper(request.user, cell)
# 	print('get_cellType ' + cellType.cell_type)
# 	results = {'success':True, 'cell_type':cellType.cell_type}
# 	return JsonResponse(results);

# @login_required
# def get_slide_json(request):
# 	GET = request.GET
# 	sid = GET['sid']
# 	slide = Slide.objects.get(sid=sid)
# 	slide_json = serializers.serialize("json", [slide])
# 	results = {'success': True, 'slide_json': slide_json}
# 	return JsonResponse(results)

    # region = Region.objects.get(rid=rid)

    # region_path = settings.MEDIA_ROOT + region.image.url
    # print(region_path)

    # # Make sure not too close to edge
    # if (center_x-box_dim/2 > 0 and center_y-box_dim/2 > 0 and \
    # 	center_x+box_dim/2 < region.width and center_y+box_dim/2 < region.height):
    # 	now = datetime.now()
    # 	date_time = now.strftime("%m%d%Y%H%M%S")
    # 	cell_path = settings.MEDIA_ROOT + '/cells/' + date_time + '.jpg'
    # 	command = "vips crop "+ region_path + " " + cell_path + " " + \
    # 		str(center_x-box_dim/2) + " " + str(center_y-box_dim/2) + " " + \
    # 		str(box_dim) + " " + str(box_dim)
    # 	os.system(command)

    # 	cell_path = '/cells/' + date_time + '.jpg'
    # 	new_cell = Cell.objects.create(region = region, image=cell_path, cid=date_time, \
    # 		center_x=center_x, center_y=center_y, width=box_dim, height=box_dim)
    # 	new_cell.save()
    # 	# cells = region.cell_set.all()
    # 	new_cell_json = serializers.serialize("json", [new_cell])
    # 	results = {'success':True, 'new_cell_json':new_cell_json}
    # else:
    # 	results = {'success':False, 'error':'too close to boundary'}

    # return JsonResponse(results)

# For label slide overlay.html which is under production
# @login_required
# def get_cell_center_relative_to_slide(request):
# 	GET = request.GET
# 	cid = GET['cid']
# 	cell = Cell.objects.get(cid=cid)
# 	results = {'success':True, 'x':cell.GetCenter_x_slide(), 'y':cell.GetCenter_y_slide()}
# 	print('get_cell_center_relative_to_slide', cell.GetCenter_x_slide(), cell.center_x,cell.GetCenter_y_slide(), cell.center_y)
# 	cell.center_x_slide = cell.GetCenter_x_slide();
# 	cell.center_y_slide = cell.GetCenter_y_slide();
# 	cell.save()
# 	print('get_cell_center_relative_to_slide', cell.GetCenter_x_slide(), cell.center_x, cell.center_x_slide, cell.GetCenter_y_slide(), cell.center_y, cell.center_y_slide)

# 	return JsonResponse(results);


# def label_cell(request, cell_id):
# 	"""label inidivudal cell"""
# 	cell = Cell.objects.get(cid=cell_id)
# 	# if request.method != 'POST':
# 	# 	form = CellLabelForm(instance=cell)

# 	# else:
# 	# 	# Post data submitted; process data
# 	# 	form = CellLabelForm(request.POST, instance=cell)
# 	# 	if form.is_valid():
# 	# 		form.save(update_fields['label', ''])
# 	region = cell.region
# 	other_cells = region.cell_set.all()
# 	context = {'region': region, 'cell':cell, 'other_cells': other_cells}
# 	return render(request, 'labeller/label_cell.html', context)

# New page started on May 7, 2021
# Rapid labeller for normal cells without associated regions

# @login_required
# def normal_cell_labeller(request):
# 	"""label all unlabelledd cells for a project"""


# 	# Need to only get cells for the current user and for the current project
# 	# For now only one user and project
# 	#NewCells = project.cell_set.all()
# 	#newCells = NewCell.objects.get()
# 	cells = NewCell.objects.all()

# 	#region = Region.objects.get(rid=region_id)
# 	#cells = region.cell_set.all()
# 	if (cells.count() == 0):
# 		cells = "none"
# 		cells_json = "none"
# 	else:
# 		cells_json = serializers.serialize("json", cells)

# 	context = {'cells':cells, 'cells_json': cells_json}
# 	print(context)
# 	return render(request, 'labeller/normal_cell_labeller.html', context)

# Experimental version that was trying to allow direct annotation on slide - big problems trying to get openseadragon to play well with Fabric.js
# @login_required
# def label_slide_overlay(request, slide_id):
# 	slide = Slide.objects.get(sid=slide_id)
# 	regions = slide.region_set.all()
# 	print(regions)
# 	cells = Cell.objects.filter(region__slide__sid=slide_id)
# 	#cells = Cell.objects.all()
# 	if (cells.count() == 0):
# 		cells_json = "none"
# 	else:
# 		cells_json = serializers.serialize("json", cells)
# 		print("cell count", cells.count())

# 	context = {'slide': slide, 'regions': regions, 'cells': cells, 'cells_json': cells_json}
# 	return render(request, 'labeller/label_slide_overlay.html', context)

# @login_required
# def new_region(request):
# 	"""Add a new region"""
# 	if request.method != 'POST':
# 		# No data submitted; create a blank form
# 		form = RegionForm()
# 	else:
# 		# POST data submitted; process data
# 		form = RegionForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return HttpResponseRedirect(reverse('labeller:regions'))

# 	context = {'form': form}
# 	return render(request, 'labeller/new_region.html', context)

# @login_required
# def blank_request(request):
# 	print(request)
# 	return JsonResponse({'success': True})

# @login_required
# def slide_viewer(request):
# 	return render(request, 'labeller/slide_viewer.html')

    # if (slide_id == '1010220220012190'):
    # 	print('1010220220012190 is being changed')
    # 	slide.dzi_path.name = 'slides/1010220220012190.dzi'
    # 	slide.save()
    # if (slide_id == '1010220220012180'):
    # 	print('1010220220012190 is being changed')
    # 	slide.dzi_path.name = 'slides/1010220220012190.dzi'
    # 	slide.save()

# if request.method == 'POST':
#     form = DiagnosisForm(request.POST)
#     if form.is_valid():
#         comment = Comment(
#             author=form.cleaned_data["author"],
#             body=form.cleaned_data["body"],
#             post=post

#         )

#         comment.save()
