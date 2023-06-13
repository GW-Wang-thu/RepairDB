from django.shortcuts import render, redirect
from django.http import HttpResponse
import pymysql
from RepairDB.models import Userinfo, Logininfo
from django.utils import timezone

# Create your views here.

def toLogin(request):
    return render(request, 'login.html')


def toIndex(requset):
    username_input = requset.POST.get("username")
    passwd_input = requset.POST.get('passwd')

    login_key = Userinfo.objects.filter(username=username_input, passwd=passwd_input).count()
    if login_key:   # 如果登录成功，渲染主页
        userid = Userinfo.objects.get(username=username_input).user_id
        temp_logininfo = Logininfo(userid=userid, date_time=timezone.now(), login_type=0)
        temp_logininfo.save()
        print(username_input, passwd_input)
        HttpResponse('登陆成功！')
        return render(requset, 'mainpage_template.html')
    else:
        return HttpResponse('登陆失败，用户名或密码错误！')


def toSearch(requset):
    print("In Search")
    return render(requset, 'data_search.html')


def toDatacollection(requset):
    return render(requset, 'data_collection.html')


def toOutreach(requset):
    return render(requset, 'DB_application.html')


def toHomepage(requset):
    return render(requset, 'user_homepage.html')