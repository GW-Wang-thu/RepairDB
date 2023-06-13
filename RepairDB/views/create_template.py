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


class SelectTemplateTypeForm(BootStrapModelForm):
    class Meta:
        model = models.TemplateInfo
        fields = ['template_type', 'template_description', 'template_title', 'template_item']


class TemplateText(BootStrapForm):
    title = forms.CharField(label="模板标题", widget=forms.TextInput, required=True)
    description = forms.CharField(label="模板描述", widget=forms.TextInput)
    content = forms.CharField(label="用户模板字段描述json", widget=forms.Textarea, required=True)


class BasicNDTForm_main(BootStrapModelForm):
    class Meta:
        model = models.NDTDataInfo
        exclude = ['data_template']


def new_template(request):
    # 渲染创建数据页面，1-选择数据大类
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    template_form = SelectTemplateTypeForm()
    if request.method == "GET":
        return render(request, "create-template.html", {"form": temp_user, "template_form": template_form})
    else:
        template_form = SelectTemplateTypeForm(data=request.POST)
        if template_form.is_valid():
            save_form = models.TemplateInfo()
            save_form.template_creator = temp_user
            # Todo: 添加审核功能
            save_form.template_status = True
            save_form.template_approver = temp_user
            save_form.template_title = template_form.cleaned_data["template_title"]
            save_form.template_item = template_form.cleaned_data["template_item"]
            save_form.template_type = template_form.cleaned_data["template_type"]
            save_form.template_description = template_form.cleaned_data["template_description"]
            save_form.template_status = 1
            save_form.save()
            template_form = SelectTemplateTypeForm()

        return render(request, "create-template.html", {"form": temp_user, "template_form": template_form})


def template_preview(request):

    if request.method == "GET":
        content = request.GET.get("template_json_str")
        print(content)
        # Todo: Json String 转成 html
        return JsonResponse({"template_html_str": content})

