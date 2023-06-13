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

class Jet_List_Selection(BootStrapModelForm):
    class Meta:
        model = models.JetInfo
        fields = ["jet_serial"]


def jet_analysis(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    jet_choices = Jet_List_Selection()
    if request.method == "GET":
        return render(request, "data-track.html", {"form": temp_user, "record_form": jet_choices})
    else:
        jet_selected = request.POST.get('jet_serial')
        print("选择查询战机：", jet_selected)
        num_defects = models.DefectInfo.objects.filter(jet_serial=jet_selected).count()
        num_defects_region1 = models.DefectInfo.objects.filter(jet_serial=jet_selected, component=0).count()
        num_defects_origin = models.DefectInfo.objects.filter(jet_serial=jet_selected, defect_origin=0).count()
        num_defects_delami = models.DefectInfo.objects.filter(jet_serial=jet_selected, defect_type=0).count()
        print("form:", temp_user,"num_defects:", num_defects, 'num_defects_region1:', num_defects_region1,
                                                  'num_defects_origin:', num_defects_origin,
                                                  'num_defects_delami:', num_defects_delami)
        return render(request, "data-track.html", {"form": temp_user,
                                                  "num_defects": num_defects,
                                                  'num_defects_region1':num_defects_region1,
                                                  'num_defects_origin':num_defects_origin,
                                                  'num_defects_delami':num_defects_delami})

#
# def new_jet(request):
#     # 渲染创建数据页面，1-选择数据大类
#     userid = request.session["info"]["id"]
#     temp_user = models.UserInfo.objects.filter(id=userid).first()
#     record_form = JetForm()
#     if request.method == "GET":
#         return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})
#     else:
#         record_form = JetForm(data=request.POST)
#         if record_form.is_valid():
#             record_form.save()
#             record_form = JetForm()
#             return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})
#         else:
#             return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})

