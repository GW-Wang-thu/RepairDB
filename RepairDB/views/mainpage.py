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




class BasicNDTForm_main(BootStrapModelForm):
    class Meta:
        model = models.NDTDataInfo
        fields = '__all__'
        # exclude = ['data_template']

class BasicREPForm_main(BootStrapModelForm):
    class Meta:
        model = models.REPDataInfo
        exclude = ['data_template']


# class BasicNDTForm_template(BootStrapModelForm):
#     class Meta:
#         model = models.NDTDataInfo
        # fields = ["data_template"]


class BasicREPForm_template(BootStrapModelForm):
    class Meta:
        model = models.REPDataInfo
        fields = ["data_template"]



def submit(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    # print(temp_user, '\n', temp_user.id, temp_user.username)
    return render(request, "mainpage_datasubmit.html", {"form": temp_user})


def service(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    return render(request, "mainpage_dataservice.html", {"form": temp_user})


def application(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    return render(request, "mainpage_dataapplication.html", {"form": temp_user})


def ndt_data_submit(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    basic_data_form = BasicNDTForm_main()
    # user_template = BasicNDTForm_template()
    # print(user_template)
    return render(request, "ndt_data_submit.html", {"form": temp_user, "data_form":basic_data_form, "utemplate":user_template})


def rep_data_submit(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    basic_data_form = BasicREPForm_main()
    user_template = BasicREPForm_template()
    # print(user_template)
    return render(request, "rep_data_submit.html",
                  {"form": temp_user, "data_form": basic_data_form, "utemplate": user_template})

#
# def jet_track(request):
#     userid = request.session["info"]["id"]
#     try:
#         session_id = request.session["info"]["id"]
#         temp_user = models.UserInfo.objects.filter(id=userid).first()
#         if int(userid) == int(session_id):
#             # Todo:
#             return render(request, "mainpage_dataapplication.html", {"form": temp_user})
#         else:
#             return redirect("/login")
#     except:
#         return redirect("/login")
#
#
# def defect_track(request):
#     userid = request.session["info"]["id"]
#     try:
#         session_id = request.session["info"]["id"]
#         temp_user = models.UserInfo.objects.filter(id=userid).first()
#         if int(userid) == int(session_id):
#             # Todo:
#             return render(request, "mainpage_dataapplication.html", {"form": temp_user})
#         else:
#             return redirect("/login")
#     except:
#         return redirect("/login")


# def datasearch(request):
#     userid = request.session["info"]["id"]
#     try:
#         session_id = request.session["info"]["id"]
#         temp_user = models.UserInfo.objects.filter(id=userid).first()
#         if int(userid) == int(session_id):
#             # Todo:
#             return render(request, "mainpage_dataapplication.html", {"form": temp_user})
#         else:
#             return redirect("/login")
#     except:
#         return redirect("/login")


# def datastatistic(request):
#     userid = request.session["info"]["id"]
#     try:
#         session_id = request.session["info"]["id"]
#         temp_user = models.UserInfo.objects.filter(id=userid).first()
#         if int(userid) == int(session_id):
#             # Todo:
#             return render(request, "mainpage_dataapplication.html", {"form": temp_user})
#         else:
#             return redirect("/login")
#     except:
#         return redirect("/login")