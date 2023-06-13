from django import forms
from django.shortcuts import render, redirect, HttpResponse
from RepairDB import models
from RepairDB.utils.bootstrap import BootStrapForm, BootStrapModelForm
from RepairDB.utils.encrypt import md5
from RepairDB.utils.img_code import check_code
from django.core.exceptions import ValidationError
from io import BytesIO
from django.utils import timezone
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class JetForm(BootStrapModelForm):
    class Meta:
        model = models.JetInfo
        fields = "__all__"


class MaintainRecForm(BootStrapModelForm):
    class Meta:
        model = models.MaintainRecInfo
        fields = "__all__"


def new_record(request):
    # 渲染创建数据页面，1-选择数据大类
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    record_form = MaintainRecForm()
    if request.method == "GET":
        return render(request, "create-record.html", {"form": temp_user, "record_form": record_form})
    else:
        record_form = MaintainRecForm(data=request.POST)
        if record_form.is_valid():
            record_form.save()
            record_form = MaintainRecForm()
            return render(request, "create-record.html", {"form": temp_user, "record_form": record_form})
        else:
            return render(request, "create-record.html", {"form": temp_user, "record_form": record_form})


def new_jet(request):
    # 渲染创建数据页面，1-选择数据大类
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    record_form = JetForm()
    if request.method == "GET":
        return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})
    else:
        record_form = JetForm(data=request.POST)
        if record_form.is_valid():
            record_form.save()
            record_form = JetForm()
            return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})
        else:
            return render(request, "create-jet.html", {"form": temp_user, "record_form": record_form})


