"""DjangoSQL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin

from django.urls import path, re_path
from RepairDB.views import account, mainpage, data_track, rep_data_submit, create_data, create_template, \
    create_record, damage_map, simulation_map, data_search, fetch_data
from DjangoSQL.settings import MEDIA_ROOT, MEDIA_URL
from django.views.static import serve
# app_name = 'RepairDB'
from django.conf.urls.static import static

urlpatterns = [
    # 登陆注销注册
    path('login/', account.login),
    path('logout/', account.logout),
    path('img_code/', account.img_code),
    path('register/', account.register),
    # 个人资料修改
    path('profile/', account.update_profile),
    path('profile/basic/', account.update_profile_basic),
    path('profile/password/', account.update_profile_password),
    path('profile/rights/', account.update_profile_rights),
    # 主页
    path('main/create-data/', mainpage.submit),
    path('main/data-service/', mainpage.service),
    path('main/data-application/', mainpage.application),

    # 创建数据
    path('create-data/new/', create_data.new_data),
    path('create-data/select-type/', create_data.select_type),
    path('create-data/select-mode/', create_data.select_upload_mode),
    path('create-data/select-template/', create_data.select_template),
    path('create-data/download-template/', create_data.download_template),
    path('create-data/submit-html/', create_data.data_submit_html),
    path('create-data/submit-json/', create_data.data_submit_json),
    # 创建模板
    path('create-data/create-template/', create_template.new_template),
    path('create-template/new/', create_template.new_template),
    # path('create-template/select-type/', create_template.select_type),
    path('create-template/preview/', create_template.template_preview),
    # 创建维护记录
    path('create-record/new/', create_record.new_record),
    path('create-jet/new/', create_record.new_jet),
    # path('create-record/select-type/', create_record.select_type),
    # path('create-record/submit/', create_record.record_submit),

    # 任务模块
    path('tasks/', account.task),
    path('tasks/my_application/', account.task_application),
    path('tasks/my_authority/', account.task_authority),
    path('task/detail/', account.task_detail),

    # 数据服务模块
    path('data-service/data_track/', data_track.query_init),
    path('data-service/data_track/query_init/', data_track.query_init),
    path('data-service/data_track/query_number/', data_track.query_number),
    path('data-service/data_track/query_size/', data_track.query_size),
    path('data-service/data_track/query_evolution/', data_track.query_evolution),
    path('data-service/data_track/query_defect/', data_track.query_defect),
    path('data-service/damage_map/', damage_map.query_init),
    path('data-service/simulation_map/', simulation_map.query_init),
    path('data-service/data_search/', data_search.jet_analysis),


]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)