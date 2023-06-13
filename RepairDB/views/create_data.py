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
from ..utils.fileio import handle_uploaded_file

NDT_data_root = r'D:\Codes\RepairDatabase\files\NDT\\'
REP_data_root = r'D:\Codes\RepairDatabase\files\REP\\'
SIMU_data_root = r'D:\Codes\RepairDatabase\files\SIMU\\'
cache_root = r'D:\Codes\RepairDatabase\files\cache\\'
NDT_file_dir = r'D:\Codes\RepairDB\RepairDatabase_v2\files\NDT\\'

class SelectDataTypeForm(BootStrapForm):
    data_types = (
        (0, "----------------------"),
        (1, "无损检测数据"),
        (2, "损伤修复数据"),
        (3, "损伤图谱数据"),
        (4, "仿真图谱数据"),
        (5, "自定义模板数据")
    )
    data_type = forms.ChoiceField(label="数据类型", widget=forms.Select(), choices=data_types, required=True, initial=data_types[0])


class Basic_NDT_Form_main(BootStrapModelForm):
    # Todo: 文件名框等，前端和后端格式内容不一致，需要修改一下
    class Meta:
        model = models.NDTDataInfo
        exclude = ['data_creator', 'data_approver', 'data_status', 'data_item_all']


class Basic_REP_Form_main(BootStrapModelForm):
    class Meta:
        model = models.REPDataInfo
        exclude = ['data_creator']


class Basic_DMAP_Form_main(BootStrapModelForm):
    class Meta:
        model = models.DMAPDataInfo
        fields = '__all__'


class Basic_SIMU_Form_main(BootStrapModelForm):
    class Meta:
        model = models.SIMUDataInfo
        exclude = ['data_creator']


class NDT_Form_All(BootStrapModelForm):
    class Meta:
        model = models.NDTDataInfo
        fields = '__all__'


class REP_Form_All(BootStrapModelForm):
    class Meta:
        model = models.REPDataInfo
        fields = '__all__'


class SIMU_Form_All(BootStrapModelForm):
    class Meta:
        model = models.SIMUDataInfo
        fields = '__all__'


def generate_template_form(template_json, template_id, return_obj=True):
    template_class_name = "C_Template_" + str(template_id)
    template_num_key = template_json["num_key"]
    des_widget = forms.Textarea(attrs={"readonly": True, "rows": 5, "placeholder": template_json["description"]})
    field_dict = {
        "description": forms.CharField(label='模板描述', widget=des_widget)
    }
    template_content = template_json["content"]
    for i in range(template_num_key):
        temp_field = template_content[str(i+1)]
        temp_field_type = temp_field["type"]
        if temp_field_type == 1:    # 填空框
            template_field_item = {str(i): forms.CharField(max_length=255, label=temp_field["name"], required=temp_field["required"])}
        elif temp_field_type == 2:
            template_field_item = {str(i): forms.FileField(allow_empty_file=temp_field["required"], label=temp_field["name"])}
        elif temp_field_type == 3:
            choices_list = temp_field["choices"]
            choices = []
            for j in range(len(choices_list)):
                choices.append((j, choices_list[j]))
            template_field_item = {str(i): forms.ChoiceField(label=temp_field["name"], widget=forms.Select(), choices=choices, required=temp_field["required"], initial=choices[0])}
        else:
            template_field_item = {}
        field_dict.update(template_field_item)
    MyTemplateFormClass = type(template_class_name, (BootStrapForm,), field_dict)
    if return_obj:
        MyTemplateFormObj = MyTemplateFormClass()
        return MyTemplateFormObj
    else:
        return MyTemplateFormClass


def generate_template_data(template_json, data_dict, files=None, save_root=None):
    if files is None:
        files = {"Voidkey": 0}
    template_num_key = template_json["num_key"]
    data_item_json = {}
    template_content = template_json["content"]
    for i in range(template_num_key):
        temp_key = str(i)
        if template_content[str(i+1)]["type"] == 2:
            tmp_file_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            tmp_file = files.get(temp_key)  # 文件
            tmp_path = tmp_file_name + str(random.randint(10000, 100000)) + "_" + tmp_file.__str__()  # 时间+随机数+真实名命名
            default_storage.save(os.path.join(save_root + "Template\\", tmp_path), ContentFile(tmp_file.read()))
            temp_field = {temp_key: tmp_path}
        else:
            temp_field = {temp_key: data_dict.get(temp_key)}
        data_item_json.update(temp_field)
    return data_item_json


# 渲染创建数据页面
def new_data(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    datatype = SelectDataTypeForm()
    if request.method == "GET":
        return render(request, "create-data.html", {"form": temp_user, "data_types": datatype})


# 响应数据大类选择的函数
def select_type(request):
    if request.method == "GET":
        data_type = request.GET.get("data_type")
        if data_type == "1":
            basic_form = Basic_NDT_Form_main()
        elif data_type == "2":
            basic_form = Basic_REP_Form_main()
        elif data_type == "3":
            basic_form = Basic_DMAP_Form_main()
        elif data_type == "4":
            basic_form = Basic_SIMU_Form_main()
        else:
            return JsonResponse({"basic_form": ''})
        basic_form_html = str(basic_form)
        return JsonResponse({"basic_form": str(basic_form_html)})


# 响应数据上传方式选择的函数
def select_upload_mode(request):
    if request.method == "GET":
        data_type = request.GET.get("data_type")
        upload_mode = request.GET.get("upload_mode")
        template_name = request.GET.get("template_name")
        if upload_mode == "form":
            # Todo: 根据基本数据类型，以及选择的用户模板，生成整体网页表单json
            form_item = {"":None}
            return JsonResponse({"form": form_item})
        elif upload_mode == "json":
            # Todo: 根据基本数据类型，以及选择的用户模板，生成上传数据模板的json文件，并预先保存到缓存区
            template_content = {"":None}
            file_name = "template" + '.json'
            file_content = json.dumps(template_content)
            f = open(os.path.join(cache_root, file_name), 'w')
            f.write(file_content)
            f.close()
            return JsonResponse({"file_name": file_name})
        else:
            ValueError("Invalid")


# 文件上传--模板下载
def download_template(request):
    if request.method == "GET":
        # 模板id
        template_id = request.GET.get('template_idx')
        # 数据类型id
        data_type = request.GET.get('datatype_idx')
        file_name = "template_demo.json"
        # # Todo: 根据数据类型获得基本条目；根据模板id获得模板条目；生成一个用于上传数据的json文件，或者excel文件
        response = FileResponse(open(os.path.join(cache_root, file_name), "rb"))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename="+file_name  # 注意filename不支持中文
        print(template_id, data_type)
        return response
        # return JsonResponse({})


# 网页上传--模板选定后
def select_template(request):
    if request.method == "GET":
        # 模板id
        template_id = request.GET.get('template_idx')
        # 数据类型id
        data_type = request.GET.get('datatype_idx')
        template_selected = models.TemplateInfo.objects.filter(template_type=int(data_type)-1, id=int(template_id))[0]
        template_item = template_selected.template_item
        template_obj = generate_template_form(template_item, template_id)
        template_html = str(template_obj)
        return JsonResponse({"template": template_html})


# 网页上传 -- 上传数据并保存
@csrf_exempt
def data_submit_html(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()

    if request.method == "POST":
        tmp_data_type = request.POST.get("data_type")
        print(tmp_data_type)
        if tmp_data_type == '1':
            submitted_data = NDT_Form_All(request.POST, request.FILES)
            if submitted_data.is_valid():
                submitted_data.instance.data_creator = temp_user
                submitted_data.save()
                tmp_record = models.NDTDataInfo.objects.last()
                # 寻找之前的缺陷
                tmp_jet = models.MaintainRecInfo.objects.filter(id=tmp_record.maintain_rec.id).last().jet_serial
                tmp_mtrecs_for_jet = models.MaintainRecInfo.objects.filter(jet_serial=tmp_jet.jet_serial)
                prev_defects = models.DefectInfo.objects.filter(maintain_rec__in=tmp_mtrecs_for_jet,
                                                                component=submitted_data.instance.component,
                                                                part=submitted_data.instance.part,
                                                                location_z_ref=submitted_data.instance.location_z_ref,
                                                                location_z_direc=submitted_data.instance.location_z_direc,
                                                                location_z_dist=submitted_data.instance.location_z_dist,
                                                                location_x_ref=submitted_data.instance.location_x_ref,
                                                                location_x_direc=submitted_data.instance.location_x_direc,
                                                                location_x_dist=submitted_data.instance.location_x_dist).order_by("id")
                if len(prev_defects) == 0:
                    defect_item = models.DefectInfo.objects.create(
                        maintain_rec=submitted_data.instance.maintain_rec,
                        component=submitted_data.instance.component,
                        part=submitted_data.instance.part,
                        location_type=submitted_data.instance.location_type,
                        location_z_ref=submitted_data.instance.location_z_ref,
                        location_z_direc=submitted_data.instance.location_z_direc,
                        location_z_dist=submitted_data.instance.location_z_dist,
                        location_x_ref=submitted_data.instance.location_x_ref,
                        location_x_direc=submitted_data.instance.location_x_direc,
                        location_x_dist=submitted_data.instance.location_x_dist,
                        location_thickness=submitted_data.instance.location_thickness,
                        size_z=submitted_data.instance.size_z,
                        size_x=submitted_data.instance.size_x,
                        defect_type=submitted_data.instance.defect_type,
                        defect_status=3,
                        next_defect=None,
                        defect_origin=submitted_data.instance.defect_origin,
                        defect_ndt_record=submitted_data.instance,
                        pre_defect=None
                    )
                    defect_item.save()
                    tmp_record.defect_item = defect_item
                    tmp_record.save()
                else:
                    last_prev = copy(prev_defects.last())
                    defect_item = models.DefectInfo.objects.create(
                        maintain_rec=submitted_data.instance.maintain_rec,
                        component=submitted_data.instance.component,
                        part=submitted_data.instance.part,
                        location_type=submitted_data.instance.location_type,
                        location_z_ref=submitted_data.instance.location_z_ref,
                        location_z_direc=submitted_data.instance.location_z_direc,
                        location_z_dist=submitted_data.instance.location_z_dist,
                        location_x_ref=submitted_data.instance.location_x_ref,
                        location_x_direc=submitted_data.instance.location_x_direc,
                        location_x_dist=submitted_data.instance.location_x_dist,
                        location_thickness=submitted_data.instance.location_thickness,
                        size_z=submitted_data.instance.size_z,
                        size_x=submitted_data.instance.size_x,
                        defect_type=submitted_data.instance.defect_type,
                        defect_status=3,
                        next_defect=None,
                        defect_origin=submitted_data.instance.defect_origin,
                        defect_ndt_record=submitted_data.instance,
                        pre_defect=last_prev.id
                    )
                    defect_item.save()
                    tmp_record.defect_item = defect_item
                    tmp_record.save()

                    last_prev.next_defect = defect_item.id
                    last_prev.save()

            #
            # post = copy(request.POST)
            # file_dict = copy(request.FILES)
            # data_type = int(post.get("data_type"))
            # # 处理文件 (形成文件名+保存文件)
            # tmp_file_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            # img_file = file_dict.get("img_path")  # 文件
            # img_path = tmp_file_name + str(random.randint(10000, 100000)) + "_" + img_file.__str__()  # 时间+随机数+真实名命名
            # # 提取基础条目
            # post.update({"data_status": 0, "data_item_all": json.dumps({"VoidKey": 0})})
            # if data_type == 1:  #无损检测数据
            #     data_item = NDT_Form_All(post, file_dict)
            #     save_root = NDT_data_root
            # elif data_type == 2:
            #     data_item = REP_Form_All(post, file_dict)
            #     save_root = REP_data_root
            # else:
            #     data_item = SIMU_Form_All(post, file_dict)
            #     save_root = SIMU_data_root
            # default_storage.save(os.path.join(save_root + "Basic\\", img_path), ContentFile(img_file.read()))
            # # 提取模板条目
            # template_id = int(post.get('data_template')[0])
            # template_item_json = models.TemplateInfo.objects.filter(template_type=int(data_type)-1,
            #                                                         id=int(template_id))[0].template_item
            # template_QDict_class = generate_template_form(template_json=template_item_json, template_id=template_id,
            #                                               return_obj=False)
            # template_data_item = template_QDict_class(post, file_dict)
            #
            # if data_item.is_valid() and template_data_item.is_valid:
            #     # 生成并保存数据
            #     template_data_json = generate_template_data(template_item_json, data_dict=template_data_item.data, files=file_dict, save_root=save_root)
            #     data_instance = models.NDTDataInfo.objects.create(
            #         data_title=data_item.cleaned_data.get("data_title"),
            #         data_description=data_item.cleaned_data.get("data_description"),
            #         maintenance_record=data_item.cleaned_data.get("maintenance_record"),
            #         data_creator=temp_user,
            #         jet_serial=data_item.cleaned_data.get("jet_serial"),
            #         defect_location_section=data_item.cleaned_data.get("defect_location_section"),
            #         defect_location=data_item.data.get("defect_location"),
            #         ndt_method=data_item.cleaned_data.get("ndt_method"),
            #         structure_type=data_item.cleaned_data.get("structure_type"),
            #         defect_type=data_item.cleaned_data.get("defect_type"),
            #         img_path=img_path,
            #         data_status=0,
            #         rep_advice=data_item.cleaned_data.get("rep_advice"),
            #         data_template=data_item.cleaned_data.get("data_template"),
            #         data_item_all=template_data_json
            #     )
            #     data_instance.save()
            #     idx = data_instance.id
            #     new_defect = True
            #     # 生成缺陷记录并保存
            #     if data_item.cleaned_data.get("rep_advice") == 1:
            #         defect_status = 0   # 无需修理
            #     else:
            #         defect_status = 1
            #     if new_defect:
            #         defect_instance = models.DefectInfo.objects.create(
            #             jet_serial=data_item.cleaned_data.get("jet_serial"),
            #             defect_location_section=data_item.cleaned_data.get("defect_location_section"),
            #             defect_location=data_item.data.get("defect_location"),
            #             defect_type=data_item.cleaned_data.get("defect_type"),
            #             defect_status=defect_status,
            #             defect_ndt_record=data_instance,
            #         )
            #         defect_instance.save()
                return JsonResponse({"status": True, "basic_data": str(submitted_data)})
            else:
                return JsonResponse({"status": False, "basic_data": str(submitted_data)})
        elif tmp_data_type == '2':
            pass
        elif tmp_data_type == '3':
            submitted_data = Basic_DMAP_Form_main(request.POST, request.FILES)
            if submitted_data.is_valid():
                submitted_data.save()
                return JsonResponse({"status": True, "basic_data": str(submitted_data)})
            else:
                return JsonResponse({"status": False, "basic_data": str(submitted_data)})

        elif tmp_data_type == '4':
            submitted_data = SIMU_Form_All(request.POST, request.FILES)
            submitted_data.instance.data_creator = temp_user
            if submitted_data.is_valid():
                submitted_data.save()
                return JsonResponse({"status": True, "basic_data": str(submitted_data)})
            else:
                return JsonResponse({"status": False, "basic_data": str(submitted_data)})


# 文件上传 -- 上传数据并保存
@csrf_exempt
def data_submit_json(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    if request.method == "POST":
        status = True
        query_dict = request.POST
        # print(request.POST)
        print(request.FILES)
        # 生成task，提交给具有审核权限的管理员，审核通过后权限生效
        if status:
            xlsx_file = request.FILES.get('file_input')
            [j_id, component, part, location_type,
             location_z_ref, location_z_dir, location_z_dis,
             location_x_ref, location_x_dir, location_x_dis,
             location_depth, size_z, size_x, defect_origin,
             defect_type, detect_stage, serve_time] = read_xlsx(xlsx_file, mode=1)
            for i in range(len(j_id)):

                # 判断是否与现有 maintain_record 符合，有则使用，无则创建
                tmp_maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial=j_id[i], record_name__contains=detect_stage[i])
                if len(tmp_maintain_rec_list) == 0:
                    return HttpResponse(json.dumps({"status": False}, ensure_ascii=False))
                else:
                    tmp_maintain_rec = tmp_maintain_rec_list.last()
                    tmp_jet = tmp_maintain_rec.jet_serial
                    tmp_mtrecs_for_jet = models.MaintainRecInfo.objects.filter(jet_serial=tmp_jet.jet_serial)
                    # 判断是否有相应 飞机 - 部件 - 零件 - 位置处，之前的检出记录
                    prev_defects = models.DefectInfo.objects.filter(maintain_rec__in=tmp_mtrecs_for_jet,
                                                                    component=component[i],
                                                                    part=part[i],
                                                                    location_z_ref=location_z_ref[i],
                                                                    location_z_direc=location_z_dir[i],
                                                                    location_z_dist=location_z_dis[i],
                                                                    location_x_ref=location_x_ref[i],
                                                                    location_x_direc=location_x_dir[i],
                                                                    location_x_dist=location_x_dis[i]).order_by("id")

                    if len(prev_defects) == 0:      # 无先前对应缺陷
                        defect_item = models.DefectInfo.objects.create(
                            maintain_rec=tmp_maintain_rec,
                            component=component[i], part=part[i], location_type=location_type[i],
                            location_z_ref=location_z_ref[i], location_z_direc=location_z_dir[i],
                            location_z_dist=location_z_dis[i],
                            location_x_ref=location_x_ref[i], location_x_direc=location_x_dir[i],
                            location_x_dist=location_x_dis[i],
                            location_thickness=location_depth[i], size_x=size_x[i], size_z=size_z[i],
                            defect_type=defect_type[i],
                            defect_origin=defect_origin[i],
                            defect_status=3,
                            next_defect=None,
                            defect_ndt_record=None,
                            pre_defect=None
                        )
                        defect_item.save()
                    else:
                        last_prev = copy(prev_defects.last())
                        defect_item = models.DefectInfo.objects.create(
                            maintain_rec=tmp_maintain_rec,
                            component=component[i], part=part[i], location_type=location_type[i],
                            location_z_ref=location_z_ref[i], location_z_direc=location_z_dir[i],
                            location_z_dist=location_z_dis[i],
                            location_x_ref=location_x_ref[i], location_x_direc=location_x_dir[i],
                            location_x_dist=location_x_dis[i],
                            location_thickness=location_depth[i], size_x=size_x[i], size_z=size_z[i],
                            defect_type=defect_type[i],
                            defect_origin=defect_origin[i],
                            defect_status=3,
                            next_defect=None,
                            defect_ndt_record=None,
                            pre_defect=last_prev.id
                        )
                        defect_item.save()
                        last_prev.next_defect = defect_item.id
                        last_prev.save()

        return HttpResponse(json.dumps({"status": status}, ensure_ascii=False))


# Todo: 写一个从json转化成HTML的函数，将数据模板
#
# def create_template(request):
#     userid = request.session["info"]["id"]
#     temp_user = models.UserInfo.objects.filter(id=userid).first()
#     template = TemplateText()
#
#     if request.method == "GET":
#         return render(request, "create-template.html", {"form": temp_user, "content": template})
#     else:
#         templateform = TemplateText(data=request.POST)
#         if templateform.is_valid():
#             title = templateform.cleaned_data["title"]
#             description = templateform.cleaned_data["description"]
#             json_string = templateform.cleaned_data["content"]
#             #
#             temp_approver = models.UserInfo.objects.filter(type=8).first()
#
#             models.Taskinfo.objects.create(task_title=temp_user.username + "创建了新的用户模板", task_type=5, task_status=0,
#                                            task_description="", task_applier=temp_user,
#                                            task_approver=temp_approver, task_create_time=timezone.now(),
#                                            task_content=json_string)
#
#             models.TemplateInfo.objects.create(template_title=title, template_status=0, template_creator=temp_user,
#                                                template_approver=temp_approver,
#                                                template_item=json_string,
#                                                template_description=description)
#             temp_approver.task_todeal = models.Taskinfo.objects.filter(task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(task_applier=temp_approver).__len__()
#             temp_approver.save()
#             temp_user.task_todeal = models.Taskinfo.objects.filter(task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(task_applier=temp_approver).__len__()
#             temp_user.save()
#             #
#         return render(request, "create-template.html", {"form": temp_user.__str__(), "content": templateform.__str__()})
#
#
# @csrf_exempt
# def data_submit(request):
#     userid = request.session["info"]["id"]
#     temp_user = models.UserInfo.objects.filter(id=userid).first()
#     if request.method == "POST":
#         status = True
#         query_dict = request.POST
#         print(request.POST)
#         print(request.FILES)
#         # 生成task，提交给具有审核权限的管理员，审核通过后权限生效
#         if status:
#             temp_approver = models.UserInfo.objects.filter(type=8).first()
#             models.Taskinfo.objects.create(task_title=temp_user.username + "提交无损检测数据", task_type=0, task_status=0,
#                                            task_description="", task_applier=temp_user,
#                                            task_approver=temp_approver, task_create_time=timezone.now(),
#                                            task_content=query_dict)
#
#             temp_approver.task_todeal = models.Taskinfo.objects.filter(
#                 task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(
#                 task_applier=temp_approver).__len__()
#             temp_approver.save()
#             temp_user.task_todeal = models.Taskinfo.objects.filter(
#                 task_approver=temp_approver).__len__() + models.Taskinfo.objects.filter(
#                 task_applier=temp_approver).__len__()
#             temp_user.save()
#
#         return HttpResponse(json.dumps({"status": status}, ensure_ascii=False))
#
#
# def ndt_data_submit_select_template(request):
#
#     if request.method == "GET":
#         template_name = request.GET.get("template_id")
#         template = models.TemplateInfo.objects.filter(id=template_name).first()
#         template_string = template.template_item
#         template_content = json.loads(template_string)
#         # print(template_content)
#
#         # class_string = '''class temp_template(BootStrapForm):\n'''
#         # my_template_content = None
#         # for i in range(template_content["content"]["num_key"]):
#         #     temp_item = template_content["content"][str(i+1)]
#         #     if temp_item["type"] == 1:
#         #         class_string += "\tinput" + str(i) + "=forms.CharField(label='"+str(temp_item["name"])+"', widget=forms.TextInput, required=True)\n"
#         #     elif temp_item["type"] == 2:
#         #         class_string += "\tinput" + str(i) + "=forms.FloatField(label='"+str(temp_item["name"])+"', widget=forms.NumberInput, required=True)\n"
#         # class_string += "my_template_content = temp_template()"
#         # class temp_template(BootStrapForm):
#         #     input0 = forms.CharField(label='检测图像', widget=forms.TextInput, required=True)
#         #     input1 = forms.FloatField(label='缺陷深度', widget=forms.NumberInput, required=True)
#
#         # my_template_content = temp_template()
#
#         # print(class_string)
#         # exec(class_string)
#         return JsonResponse({"template": template_content})

    # return JsonResponse({"status":True})


