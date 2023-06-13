import random

from django import forms
from django.shortcuts import render, redirect, HttpResponse
from RepairDB import models
from RepairDB.utils.bootstrap import BootStrapForm, BootStrapModelForm
from django.utils import timezone
import json
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.core import serializers
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from copy import copy
from ..utils.xlsx_parser import read_xlsx

NDT_data_root = r'D:\Codes\RepairDatabase\files\NDT\\'
REP_data_root = r'D:\Codes\RepairDatabase\files\REP\\'
SIMU_data_root = r'D:\Codes\RepairDatabase\files\SIMU\\'
cache_root = r'D:\Codes\RepairDatabase\files\cache\\'


class SIMUMap(BootStrapModelForm):
    class Meta:
        model = models.DMAPDataInfo
        fields = ["structure_type", 'ndt_method', 'damage_type']


def query_init(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    jet_choices = SIMUMap()
    if request.method == "GET":
        return render(request, "simulation_map.html", {"form": temp_user, "dmap_form": jet_choices})
    else:
        print(request.POST)
        structure_type = request.POST.get('structure_type')
        structure_object = request.POST.get('structure_object')
        simulation_software = request.POST.get('simulation_software')
        load_type = request.POST.get('load_type')
        print(structure_type, structure_object, simulation_software, load_type)
        q_items = models.SIMUDataInfo.objects.all()
        if structure_type != '0':
            q_items = q_items.filter(structure_type=int(structure_type)-1)
        if structure_object != '0':
            q_items = q_items.filter(structure_object=int(structure_object)-1)
        if simulation_software != '0':
            q_items = q_items.filter(simulation_software=int(simulation_software)-1)
        if load_type != '0':
            q_items = q_items.filter(load_type=int(load_type)-1)
        num_items = q_items.count()
        fed_imgs = []
        for item in q_items:
            tmp_dict = {"title": item.data_title, 'description': item.data_description, 'imgdir': item.demo_img.__str__()}
            fed_imgs.append(tmp_dict)
        print(num_items, fed_imgs)
        return JsonResponse({"num_items": num_items, 'fed_imgs': fed_imgs})

