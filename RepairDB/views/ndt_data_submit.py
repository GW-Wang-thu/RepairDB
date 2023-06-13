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


class TemplateText(BootStrapForm):
    title = forms.CharField(label="模板标题", widget=forms.TextInput, required=True)
    description = forms.CharField(label="模板描述", widget=forms.TextInput)
    content = forms.CharField(label="用户模板字段描述json", widget=forms.Textarea, required=True)



class BasicNDTForm_main(BootStrapModelForm):
    class Meta:
        model = models.NDTDataInfo
        exclude = ['data_template']


def create_template(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    template = TemplateText()

    if request.method == "GET":
        return render(request, "create-template.html", {"form": temp_user, "content": template})
    else:
        templateform = TemplateText(data=request.POST)
        if templateform.is_valid():
            title = templateform.cleaned_data["title"]
            description = templateform.cleaned_data["description"]
            json_string = templateform.cleaned_data["content"]
            #
            temp_approver = models.UserInfo.objects.filter(type=8).first()

            models.Taskinfo.objects.create(task_title=temp_user.username + "创建了新的用户模板", task_type=5, task_status=0,
                                           task_description="", task_applier=temp_user,
                                           task_approver=temp_approver, task_create_time=timezone.now(),
                                           task_content=json_string)

            models.TemplateInfo.objects.create(template_title=title, template_status=0, template_creator=temp_user,
                                               template_approver=temp_approver,
                                               template_item=json_string,
                                               template_description=description)
            temp_approver.task_todeal = models.Taskinfo.objects.filter(task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(task_applier=temp_approver).__len__()
            temp_approver.save()
            temp_user.task_todeal = models.Taskinfo.objects.filter(task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(task_applier=temp_approver).__len__()
            temp_user.save()
            #
        return render(request, "create-template.html", {"form": temp_user, "content": templateform})


@csrf_exempt
def ndt_data_submit(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    if request.method == "POST":
        status = True
        query_dict = request.POST
        print(request.POST)
        print(request.FILES)
        # 生成task，提交给具有审核权限的管理员，审核通过后权限生效
        if status:
            temp_approver = models.UserInfo.objects.filter(type=8).first()
            models.Taskinfo.objects.create(task_title=temp_user.username + "提交无损检测数据", task_type=0, task_status=0,
                                           task_description="", task_applier=temp_user,
                                           task_approver=temp_approver, task_create_time=timezone.now(),
                                           task_content=query_dict)

            temp_approver.task_todeal = models.Taskinfo.objects.filter(
                task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(
                task_applier=temp_approver).__len__()
            temp_approver.save()
            temp_user.task_todeal = models.Taskinfo.objects.filter(
                task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(
                task_applier=temp_approver).__len__()
            temp_user.save()

        return HttpResponse(json.dumps({"status": status}, ensure_ascii=False))


def ndt_data_submit_select_template(request):

    if request.method == "GET":
        template_name = request.GET.get("template_id")
        template = models.TemplateInfo.objects.filter(id=template_name).first()
        template_string = template.template_item
        template_content = json.loads(template_string)
        # print(template_content)

        # class_string = '''class temp_template(BootStrapForm):\n'''
        # my_template_content = None
        # for i in range(template_content["content"]["num_key"]):
        #     temp_item = template_content["content"][str(i+1)]
        #     if temp_item["type"] == 1:
        #         class_string += "\tinput" + str(i) + "=forms.CharField(label='"+str(temp_item["name"])+"', widget=forms.TextInput, required=True)\n"
        #     elif temp_item["type"] == 2:
        #         class_string += "\tinput" + str(i) + "=forms.FloatField(label='"+str(temp_item["name"])+"', widget=forms.NumberInput, required=True)\n"
        # class_string += "my_template_content = temp_template()"
        # class temp_template(BootStrapForm):
        #     input0 = forms.CharField(label='检测图像', widget=forms.TextInput, required=True)
        #     input1 = forms.FloatField(label='缺陷深度', widget=forms.NumberInput, required=True)

        # my_template_content = temp_template()

        # print(class_string)
        # exec(class_string)
        return JsonResponse({"template": template_content})

    # return JsonResponse({"status":True})
