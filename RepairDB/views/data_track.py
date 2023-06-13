import random

import numpy as np
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
import scipy.stats as stats

NDT_data_root = r'D:\Codes\RepairDatabase\files\NDT\\'
REP_data_root = r'D:\Codes\RepairDatabase\files\REP\\'
SIMU_data_root = r'D:\Codes\RepairDatabase\files\SIMU\\'
cache_root = r'D:\Codes\RepairDatabase\files\cache\\'


def default_dump(obj):
    """Convert numpy classes to JSON serializable objects."""
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


class Jet_List_Selection(BootStrapModelForm):
    class Meta:
        model = models.JetInfo
        fields = ["jet_serial"]


def q_init():
    defect_list = models.DefectInfo.objects.all().order_by('id')
    jids = []
    jtypes = []
    serve_areas = []
    maintain_recs = []

    components = []
    parts = []
    damage_types = []
    location_types = []

    for defect in defect_list:
        # 飞机相关
        maintain_rec = defect.maintain_rec
        jet = maintain_rec.jet_serial
        maintain_recs.append(maintain_rec.__str__())
        jtypes.append(str(jet.jet_types[jet.jet_type][0]) + '-' + jet.jet_types[jet.jet_type][1])
        jids.append(jet.jet_serial)
        serve_areas.append(jet.jet_serve_region)
        # 缺陷相关
        components.append(str(defect.components[defect.component][0]) + '-' + defect.components[defect.component][1])
        parts.append(str(defect.parts[defect.part][0]) + '-' + defect.parts[defect.part][1])
        damage_types.append(str(defect.defect_types[defect.defect_type][0]) + '-' + defect.defect_types[defect.defect_type][1])
        location_types.append(str(defect.location_types[defect.location_type][0]) + '-' + defect.location_types[defect.location_type][1])

    return list(set(jtypes)), list(set(serve_areas)), list(set(jids)), list(set(components)), \
            list(set(parts)), list(set(maintain_recs)), list(set(damage_types)), list(set(location_types))


def query_init(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    jet_choices = Jet_List_Selection()
    if request.method == "GET":
        return render(request, "data-track.html", {"form": temp_user, "record_form": jet_choices})
    else:
        jtypes, serve_areas, jids, components, parts, serve_time, damage_types, location_types = q_init()
        return JsonResponse({"jtype": jtypes, "serve_area": serve_areas, "jid": jids, "jcomp": components,
                             "jpart": parts, "detect_time": serve_time, "defect_type": damage_types,
                             "location_type": location_types})


def calculate_distribution(data, model):
    models = ["auto", "log-exp", "Weibull", "Rayleigh", "Gama"]
    dist_law = models[model]
    if model == 0:
        dist_law = models[1]
    hist, bins = np.histogram(data, bins=50)
    step = bins[1] - bins[0]        # 频率直方图的横坐标步长为1，而实际比1大，为了让累计频次面积相等，将回归模型的频率*step
    integral = []
    sum = 0
    hist = hist / np.sum(hist)
    for i in range(len(hist)):
        integral.append(hist[i] + sum)
        sum += hist[i]
    if dist_law == 'log-exp':
        log_std = np.std(np.log(data))
        log_mean = np.mean(np.log(data))
        dist = step * np.exp(-(np.log(bins)-log_mean)**2/(2*log_std**2))/(bins * log_std * np.sqrt(2.0*np.pi))
        dist_sets = dist.tolist()
    else:
        a, c = stats.exponweib.fit(data)
        dist = stats.exponweib.pdf(bins, a, c)
        dist_sets = dist.tolist()

    return np.round(bins, 1).tolist(), hist.tolist(), integral, dist_sets, dist_law


def make_fig_number(request):
    jtypes, serve_areas, jids, components, parts, serve_time, defect_types, location_types = q_init()
    x_keys = []
    jtype_selected = None
    serve_area_selected = None
    jid_selected = None
    component_selected = None
    part_selected = None
    detect_time_selected = None
    defect_type_selected = None
    location_type_selected = None
    if int(request['jtype'][0]) > 1:
        jtype_selected = int(jtypes[int(request['jtype'][0]) - 2].split('-')[0])
    else:
        if int(request['jtype'][0]):
            x_keys.append('jtypes')
    if int(request['serve_area'][0]) > 1:
        serve_area_selected = serve_areas[int(request['serve_area'][0]) - 2]
    else:
        if int(request['serve_area'][0]):
            x_keys.append('serve_areas')
    if int(request['jid'][0]) > 1:
        jid_selected = jids[int(request['jid'][0]) - 2]
    else:
        if int(request['jid'][0]):
            x_keys.append('jids')
    if int(request['jcomp'][0]) > 1:
        component_selected = int(components[int(request['jcomp'][0]) - 2].split('-')[0])
    else:
        if int(request['jcomp'][0]):
            x_keys.append('components')
    if int(request['jpart'][0]) > 1:
        part_selected = int(parts[int(request['jpart'][0]) - 2].split('-')[0])
    else:
        if int(request['jpart'][0]):
            x_keys.append('parts')
    if int(request['detect_time'][0]) > 1:
        detect_time_selected = serve_time[int(request['detect_time'][0]) - 2]
    else:
        if int(request['detect_time'][0]):
            x_keys.append('detection_time')
    if int(request['defect_type'][0]) > 1:
        defect_type_selected = int(defect_types[int(request['defect_type'][0]) - 2].split('-')[0])
    else:
        if int(request['defect_type'][0]):
            x_keys.append('defect_types')
    if int(request['location_type'][0]) > 1:
        location_type_selected = int(location_types[int(request['location_type'][0]) - 2].split('-')[0])
    else:
        if int(request['location_type'][0]):
            x_keys.append('location_types')

    qd = models.DefectInfo.objects.all()
    if jtype_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_type=jtype_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if serve_area_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_serve_region=serve_area_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if jid_selected is not None:
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial=jid_selected.split(":")[-1])
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if component_selected is not None:
        qd = qd.filter(component=component_selected)
    if part_selected is not None:
        qd = qd.filter(part=component_selected)
    if detect_time_selected is not None:
        qd = qd.filter(maintain_rec_id=int(detect_time_selected.split('-')[0]))
    if defect_type_selected is not None:
        qd = qd.filter(defect_type=defect_type_selected)
    if location_type_selected is not None:
        qd = qd.filter(location_type=location_type_selected)
    if len(x_keys) == 0:
         x_keys = ["all"]
    json_list = {}
    for key in x_keys:
        tmp_title = "缺陷统计"
        tmp_legend = ["all"]
        tmp_series_data = []
        x_axis = ["all"]
        if key == "all":
            tmp_series_data.append(qd.count())
        elif key == "jtypes":
            x_axis = jtypes
            for type in jtypes:
                tmp_title = "缺陷统计(按机型)"
                type = int(type.split('-')[0])
                jet_list = models.JetInfo.objects.filter(jet_type=type)
                tmp_maintain_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
                tmp_data = qd.filter(maintain_rec__in=tmp_maintain_list).count()
                tmp_series_data.append(tmp_data)
        elif key == 'serve_areas':
            tmp_title = "缺陷统计(按服役地区)"
            x_axis = serve_areas
            for area in serve_areas:
                jet_list = models.JetInfo.objects.filter(jet_serve_region=area)
                tmp_maintain_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
                tmp_series_data.append(qd.filter(maintain_rec__in=tmp_maintain_list).count())
        elif key == 'jids':
            tmp_title = "缺陷统计(按架次)"
            x_axis = jids
            for jid in jids:
                tmp_maintain_list = models.MaintainRecInfo.objects.filter(jet_serial=jid.split(":")[-1])
                tmp_series_data.append(qd.filter(maintain_rec__in=tmp_maintain_list).count())
        elif key == 'components':
            tmp_title = "缺陷统计(按部件)"
            x_axis = components
            for component in components:
                tmp_series_data.append(qd.filter(component=int(component.split('-')[0])).count())
        elif key == 'parts':
            tmp_title = "缺陷统计(按零件)"
            x_axis = parts
            for part in parts:
                tmp_series_data.append(qd.filter(part=int(part.split('-')[0])).count())
        elif key == 'detection_time':
            tmp_title = "缺陷统计(按检测时的飞行时间)"
            x_axis = serve_time
            for flight_time in serve_time:
                tmp_series_data.append(qd.filter(maintain_rec_id=int(flight_time.split('-')[0])).count())
        elif key == 'defect_type':
            tmp_title = "缺陷统计(按缺陷类型)"
            x_axis = defect_types
            for defect_type in defect_types:
                tmp_series_data.append(qd.filter(defect_type=int(defect_type.split('-')[0])).count())
        elif key == 'location_types':
            tmp_title = "缺陷统计(按缺陷位置类型)"
            x_axis = location_types
            for location_type in location_types:
                tmp_series_data.append(qd.filter(location_type=int(location_type.split('-')[0])).count())
        tmp_json = {"title": tmp_title, "legend":tmp_legend, "x_axis":x_axis, "series": tmp_series_data}
        json_list.update({key: tmp_json})
    return json_list


def make_fig_size(request):
    jtypes, serve_areas, jids, components, parts, serve_time, defect_types, location_types = q_init()
    x_keys = ['length', 'width', 'area', 'aspect']
    jtype_selected = None
    serve_area_selected = None
    jid_selected = None
    component_selected = None
    part_selected = None
    detect_time_selected = None
    defect_type_selected = None
    location_type_selected = None
    print(request)
    if int(request['jtype'][0]) > 0:
        jtype_selected = int(jtypes[int(request['jtype'][0]) - 2].split('-')[0])
    if int(request['serve_area'][0]) > 0:
        serve_area_selected = serve_areas[int(request['serve_area'][0]) - 2]
    if int(request['jid'][0]) > 0:
        jid_selected = jids[int(request['jid'][0]) - 2]
    if int(request['jcomp'][0]) > 0:
        component_selected = int(components[int(request['jcomp'][0]) - 2].split('-')[0])
    if int(request['jpart'][0]) > 0:
        part_selected = int(parts[int(request['jpart'][0]) - 2].split('-')[0])
    if int(request['detect_time'][0]) > 0:
        detect_time_selected = serve_time[int(request['detect_time'][0]) - 2]
    if int(request['defect_type'][0]) > 0:
        defect_type_selected = int(defect_types[int(request['defect_type'][0]) - 2].split('-')[0])
    if int(request['location_type'][0]) > 0:
        location_type_selected = int(location_types[int(request['location_type'][0]) - 2].split('-')[0])

    qd = models.DefectInfo.objects.all()
    if jtype_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_type=jtype_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if serve_area_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_serve_region=serve_area_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if jid_selected is not None:
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial=jid_selected.split(":")[-1])
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if component_selected is not None:
        qd = qd.filter(component=component_selected)
    if part_selected is not None:
        qd = qd.filter(part=component_selected)
    if detect_time_selected is not None:
        qd = qd.filter(maintain_rec_id=int(detect_time_selected.split('-')[0]))
    if defect_type_selected is not None:
        qd = qd.filter(defect_type=defect_type_selected)
    if location_type_selected is not None:
        qd = qd.filter(location_type=location_type_selected)

    json_list = {}
    for key in x_keys:
        if key == 'length':
            data = [item.size_x for item in qd]
            x_sets, data_sets, integral_sets, dist_sets, law = calculate_distribution(data, int(request['distribution_law'][0]))
            tmp_title = '展向长度分布（样本数%d）'%(len(data))
            tmp_legend = ["区间分布", "缺陷累计", law + "回归的分布"]
            tmp_unit = ' mm'
            json_list.update({key: {
                'title': tmp_title,
                'legend': tmp_legend,
                'x_axis': x_sets,
                'unit': tmp_unit,
                'data_item': data_sets,
                'data_integral': integral_sets,
                'dist_law': dist_sets
            }
            })
        elif key == 'width':
            data = [item.size_z for item in qd]
            x_sets, data_sets, integral_sets, dist_sets, law = calculate_distribution(data, int(request['distribution_law'][0]))
            tmp_title = '弦向长度分布（样本数%d）'%(len(data))
            tmp_legend = ["区间分布", "缺陷累计", law + "回归的分布"]
            tmp_unit = ' mm'
            json_list.update({key: {
                'title': tmp_title,
                'legend': tmp_legend,
                'x_axis': x_sets,
                'unit': tmp_unit,
                'data_item': data_sets,
                'data_integral': integral_sets,
                'dist_law': dist_sets
            }
            })
        elif key == 'area':
            data = [item.size_z * item.size_x for item in qd]
            x_sets, data_sets, integral_sets, dist_sets, law = calculate_distribution(data, int(request['distribution_law'][0]))
            tmp_title = '缺陷面积分布（样本数%d）'%(len(data))
            tmp_legend = ["区间分布", "缺陷累计", law + "回归的分布"]
            tmp_unit = ' mm2'
            json_list.update({key: {
                'title': tmp_title,
                'legend': tmp_legend,
                'x_axis': x_sets,
                'unit': tmp_unit,
                'data_item': data_sets,
                'data_integral': integral_sets,
                'dist_law': dist_sets
            }
            })
        elif key == 'aspect':
            data1 = [item.size_z / item.size_x for item in qd if (item.size_z > item.size_x)]
            data2 = [item.size_x / item.size_z for item in qd if (item.size_z <= item.size_x)]
            data = data1 + data2
            x_sets, data_sets, integral_sets, dist_sets, law = calculate_distribution(data, int(request['distribution_law'][0]))
            tmp_title = '缺陷长宽比分布（样本数%d）'%(len(data))
            tmp_legend = ["区间分布", "频次累计", law + "回归的分布"]
            tmp_unit = ''
            json_list.update({key: {
                'title': tmp_title,
                'legend': tmp_legend,
                'x_axis': x_sets,
                'unit': tmp_unit,
                'data_item': data_sets,
                'data_integral': integral_sets,
                'dist_law': dist_sets
            }
            })
    json_list = json.dumps(json_list, default=default_dump)
    return json.loads(json_list)


def make_fig_evolution(request):
    jtypes, serve_areas, jids, components, parts, _, defect_types, location_types = q_init()
    jtype_selected = None
    serve_area_selected = None
    jid_selected = None
    component_selected = None
    part_selected = None
    defect_type_selected = None
    location_type_selected = None
    x_keys = ['main']
    print(request)
    if int(request['jtype'][0]) > 0:
        jtype_selected = int(jtypes[int(request['jtype'][0]) - 2].split('-')[0])
    if int(request['serve_area'][0]) > 0:
        serve_area_selected = serve_areas[int(request['serve_area'][0]) - 2]
    if int(request['jid'][0]) > 0:
        jid_selected = jids[int(request['jid'][0]) - 2]
    if int(request['jcomp'][0]) > 0:
        component_selected = int(components[int(request['jcomp'][0]) - 2].split('-')[0])
    if int(request['jpart'][0]) > 0:
        part_selected = int(parts[int(request['jpart'][0]) - 2].split('-')[0])
    if int(request['defect_type'][0]) > 0:
        defect_type_selected = int(defect_types[int(request['defect_type'][0]) - 2].split('-')[0])
    if int(request['location_type'][0]) > 0:
        location_type_selected = int(location_types[int(request['location_type'][0]) - 2].split('-')[0])
    func_type_selected = int(request['evolution_law'][0])
    if func_type_selected == 0: # 线性
        func_type = {'method': 'polynomial', 'order': 1}
    elif func_type_selected == 1:   # 二次
        func_type = {'method': 'polynomial', 'order': 2}
    elif func_type_selected == 2:   # 指数
        func_type = {'method': 'exponential'}

    else:
        func_type = {}

    qd = models.DefectInfo.objects.all()
    if jtype_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_type=jtype_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if serve_area_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_serve_region=serve_area_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if jid_selected is not None:
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial=jid_selected.split(":")[-1])
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if component_selected is not None:
        qd = qd.filter(component=component_selected)
    if part_selected is not None:
        qd = qd.filter(part=component_selected)
    if defect_type_selected is not None:
        qd = qd.filter(defect_type=defect_type_selected)
    if location_type_selected is not None:
        qd = qd.filter(location_type=location_type_selected)
    # 筛选所有新发缺陷
    qd = qd.filter(pre_defect=None)
    # 统计新发 缺陷-时间 关系
    all_flight_time = []
    for defect in qd:
        all_flight_time.append(float(defect.maintain_rec.flight_time))
    all_flight_time_set = set(all_flight_time)
    all_ft_array = np.array(all_flight_time)
    data = []
    for ft in all_flight_time_set:
        num_ft = np.sum((all_ft_array - ft) == 0)
        data.append([ft, num_ft])
    # 按时间排序，积分
    data = np.array(data)
    data_sort = data[np.argsort(data[:, 0])].tolist()
    integ_data = []
    sum = 0
    for pair in data_sort:
        integ_data.append([float(pair[0]), sum + int(pair[1])])
        sum += int(pair[1])

    json_list = {}
    for key in x_keys:
        tmp_title = '总缺陷数量演化曲线'
        json_list.update({key: {
            'title': tmp_title,
            'data': integ_data,
            'func_type': func_type
        }
        })
    json_list = json.dumps(json_list, default=default_dump)
    return json.loads(json_list)


def make_table_defect_track(request):
    jtypes, serve_areas, jids, components, parts, _, defect_types, location_types = q_init()
    jtype_selected = None
    serve_area_selected = None
    jid_selected = None
    component_selected = None
    part_selected = None
    defect_type_selected = None
    location_type_selected = None
    x_keys = ['main']
    print(request)
    if int(request['jtype'][0]) > 0:
        jtype_selected = int(jtypes[int(request['jtype'][0]) - 2].split('-')[0])
    if int(request['serve_area'][0]) > 0:
        serve_area_selected = serve_areas[int(request['serve_area'][0]) - 2]
    if int(request['jid'][0]) > 0:
        jid_selected = jids[int(request['jid'][0]) - 2]
    if int(request['jcomp'][0]) > 0:
        component_selected = int(components[int(request['jcomp'][0]) - 2].split('-')[0])
    if int(request['jpart'][0]) > 0:
        part_selected = int(parts[int(request['jpart'][0]) - 2].split('-')[0])
    if int(request['defect_type'][0]) > 0:
        defect_type_selected = int(defect_types[int(request['defect_type'][0]) - 2].split('-')[0])
    if int(request['location_type'][0]) > 0:
        location_type_selected = int(location_types[int(request['location_type'][0]) - 2].split('-')[0])

    qd = models.DefectInfo.objects.all()
    if jtype_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_type=jtype_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if serve_area_selected is not None:
        jet_list = models.JetInfo.objects.filter(jet_serve_region=serve_area_selected)
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial__in=jet_list)
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if jid_selected is not None:
        maintain_rec_list = models.MaintainRecInfo.objects.filter(jet_serial=jid_selected.split(":")[-1])
        qd = qd.filter(maintain_rec__in=maintain_rec_list)
    if component_selected is not None:
        qd = qd.filter(component=component_selected)
    if part_selected is not None:
        qd = qd.filter(part=component_selected)
    if defect_type_selected is not None:
        qd = qd.filter(defect_type=defect_type_selected)
    if location_type_selected is not None:
        qd = qd.filter(location_type=location_type_selected)
    # 筛选所有新发缺陷
    qd = qd.filter(pre_defect=None)
    defect_list = []
    for defect in qd:
        temp_dict = {
            "id": defect.id,
            "jid": defect.maintain_rec.jet_serial.__str__(),
            "component": defect.components[defect.component][1],
            "part": defect.parts[defect.part][1],
            "location_type": defect.location_types[defect.location_type][1],
            "type": defect.defect_types[defect.defect_type][1],
            "origin_time": defect.maintain_rec.start_date,
        }
        defect_list.append(temp_dict)

    return {"defect_list": defect_list}

def make_figure_defect_track(defect_id):
    x_data = []
    size_x = []
    size_z = []
    depth = []
    area = []
    tmp_defect_id = defect_id
    while (tmp_defect_id is not None):
        tmp_defect = models.DefectInfo.objects.filter(id=tmp_defect_id).first()
        x_data.append(tmp_defect.maintain_rec.flight_time)
        size_x.append(tmp_defect.size_x)
        size_z.append(tmp_defect.size_z)
        area.append(tmp_defect.size_x * tmp_defect.size_z)
        depth.append(tmp_defect.location_thickness)
        tmp_defect_id = tmp_defect.next_defect
    return {"flight_time": x_data, "size_x": size_x, "size_z": size_z, "area": area}


def query_number(request):
    if request.method == "GET":
        pass
    else:
        fig_json = make_fig_number(request.POST)
        return JsonResponse(fig_json)


def query_size(request):
    if request.method == "GET":
        pass
    else:
        fig_json = make_fig_size(request.POST)
        print(fig_json)
        return JsonResponse(fig_json)


def query_evolution(request):
    if request.method == "GET":
        pass
    else:
        fig_json = make_fig_evolution(request.POST)
        print(fig_json)
        return JsonResponse(fig_json)


def query_defect(request):
    if request.method == "GET":
        figure_json = make_figure_defect_track(request.GET.get('defect_id'))
        return JsonResponse(figure_json)
    else:
        table_json = make_table_defect_track(request.POST)
        return JsonResponse(table_json)



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

