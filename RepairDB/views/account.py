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
from django.core import serializers


class LoginForm(BootStrapModelForm):
    img_code = forms.CharField(label="图片验证码", widget=forms.TextInput, required=True)

    class Meta:
        model = models.UserInfo
        fields = ['username', 'passwd', 'img_code']
        widgets = {
            "passwd": forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("passwd")
        return md5(pwd)


class RegisterForm(BootStrapModelForm):
    passwd_repeat = forms.CharField(label="再次输入密码", max_length=255, widget=forms.PasswordInput, required=True)

    class Meta:
        model = models.UserInfo
        fields = ['mail', 'username', 'passwd', 'passwd_repeat']
        widgets = {
            "passwd": forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("passwd")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = md5(self.cleaned_data.get("passwd"))
        confirm = md5(self.cleaned_data.get("passwd_repeat"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        # 返回什么，此字段以后保存到数据库就是什么。
        return confirm


class EditprofileForm_basic(BootStrapModelForm):

    class Meta:
        model = models.UserInfo
        fields = ['username', 'mail', 'ecard_id']


class EditprofileForm_password(BootStrapForm):
    passwd_old = forms.CharField(label="输入旧密码", max_length=255, widget=forms.PasswordInput, required=True)
    passwd = forms.CharField(label="输入新密码", max_length=255, widget=forms.PasswordInput, required=True)
    passwd_repeat = forms.CharField(label="再次输入密码", max_length=255, widget=forms.PasswordInput, required=True)

    def clean_passwd(self):
        pwd = self.cleaned_data.get("passwd")
        if pwd == self.cleaned_data.get("passwd_old"):
            raise ValidationError("不能与原密码一致")
        return pwd

    def clean_passwd_old(self):
        pwd = self.cleaned_data.get("passwd_old")

        return pwd

    def clean_passwd_repeat(self):
        pwd = self.cleaned_data.get("passwd")
        confirm = self.cleaned_data.get("passwd_repeat")
        if confirm != pwd and pwd is not None:
            print(pwd, confirm, self.cleaned_data.get("passwd"), self.cleaned_data.get("passwd_repeat"))
            raise ValidationError("密码不一致")
        return confirm


class EditprofileForm_rights(BootStrapForm):
    description = forms.CharField(label="申请说明和备注", max_length=500, widget=forms.Textarea, required=False)
    right_keys = forms.CharField(label="使用权限码激活", max_length=25, widget=forms.TextInput, required=False)


class TaskForm(BootStrapModelForm):
    class Meta:
        model = models.Taskinfo
        fields = ['task_title', 'task_type', 'task_status', 'task_applier', 'task_approver', 'task_create_time',
                  'task_decision_time', 'task_description']


def login(request):
    if request.method == "GET":
        try:
            userid = request.session["info"]["id"]
            return redirect('/main/create-data/')
        except:
            pass
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user_input_code = form.cleaned_data.pop('img_code')
            code = request.session.get('img_code', "")
            if code != str(user_input_code):
                form.add_error("img_code", "验证码错误")
                return render(request, 'login.html', {'form': form})

            # 去数据库校验用户名和密码是否正确，获取用户对象、None
            user_object = models.UserInfo.objects.filter(
                **{'username': form.cleaned_data["username"], 'passwd': form.clean_password()}).first()
            if not user_object:
                form.add_error("passwd", "用户名或密码错误")
                # form.add_error("username", "用户名或密码错误")
                return render(request, 'login.html', {'form': form})
            # 用户名和密码正确
            # 网站生成随机字符串; 写到用户浏览器的cookie中；在写入到session中；
            request.session["info"] = {'id': user_object.id, 'name': user_object.username}
            # session可以保存7天
            request.session.set_expiry(60 * 24 * 7)  # 60 * 24 * 7 1小时
            messages.success(request, "登陆成功")
            return redirect('/main/create-data/')

        return render(request, 'login.html', {'form': form})
        # Todo: 判断


def img_code(requset):
    img, code_string = check_code()
    requset.session["img_code"] = code_string
    stream = BytesIO()
    img.save(stream, 'png')
    # print(stream.getvalue())
    return HttpResponse(stream.getvalue())


def logout(request):
    try:
        del request.session["info"]
        form = LoginForm()
        return redirect("/login/", {'form': form})
    except:
        form = LoginForm()
        return redirect("/login/", {'form': form})


def task(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    if request.method == "GET":
        return render(request, 'task.html', {"form": temp_user})


@csrf_exempt
def task_application(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()

    if request.method == "GET":
        temp_task_qs = models.Taskinfo.objects.filter(task_applier=temp_user)
        tabel_item_dict = {}
        i = 0
        print(temp_task_qs)
        for temp_instance in temp_task_qs:
            i += 1
            temp_task_info_dict = {
                "id": temp_instance.id,
                "type": temp_instance.task_type,
                "title": temp_instance.task_title,
                "applier": temp_instance.task_applier.username,
                "create_time": str(temp_instance.task_create_time),
                "status": temp_instance.task_status,
            }
            tabel_item_dict.update({"task" + str(i): temp_task_info_dict})
        return HttpResponse(json.dumps({"tabel_item": tabel_item_dict, "status": True}, ensure_ascii=False))

    if request.method == "POST":
        return_form = EditprofileForm_basic(data=request.POST, instance=temp_user)
        status = False
        if return_form.is_valid():
            return_form.save()
            status = True

        return HttpResponse(json.dumps({"status": status, "errors": return_form.errors}, ensure_ascii=False))


@csrf_exempt
def task_detail(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()

    if request.method == "GET":
        temp_task_id = request.GET.get("taskid")
        tabel_item_dict = {}
        return HttpResponse(json.dumps({"tabel_item": tabel_item_dict, "status": True}, ensure_ascii=False))

@csrf_exempt
def task_authority(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()

    if request.method == "GET":
        temp_task_qs = models.Taskinfo.objects.filter(task_approver=temp_user)
        tabel_item_dict = {}
        i = 0
        for temp_instance in temp_task_qs:
            i += 1
            temp_task_info_dict = {
                "id": temp_instance.id,
                "type": temp_instance.task_type,
                "title": temp_instance.task_title,
                "applier": temp_instance.task_applier.username,
                "create_time": str(temp_instance.task_create_time),
                "status": temp_instance.task_status,
            }
            tabel_item_dict.update({"task" + str(i): temp_task_info_dict})
        return HttpResponse(json.dumps({"tabel_item": tabel_item_dict, "status": True}, ensure_ascii=False))

    if request.method == "POST":
        return_form = EditprofileForm_basic(data=request.POST, instance=temp_user)
        status = False
        if return_form.is_valid():
            return_form.save()
            status = True

        return HttpResponse(json.dumps({"status": status, "errors": return_form.errors}, ensure_ascii=False))


def register(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "register.html", {'form': form})

    else:
        form = RegisterForm(data=request.POST)

        if form.is_valid():

            if form.clean_password() != form.clean_confirm_password():
                form.add_error("passwd_repeat", "密码不一致")
                return render(request, 'register.html', {'form': form})

            models.UserInfo.objects.create(username=form.cleaned_data["username"],
                                           join_date=timezone.now(),
                                           passwd=form.clean_confirm_password(),
                                           mail=form.cleaned_data["mail"])
            return redirect('/login/')

        return render(request, 'register.html', {'form': form})


@csrf_exempt
def update_profile(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    if request.method == "GET":
        return render(request, 'edit_profile.html', {"form": temp_user})


@csrf_exempt
def update_profile_basic(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    basic_form = EditprofileForm_basic(instance=temp_user)
    if request.method == "GET":
        return HttpResponse(json.dumps({"basic_form": str(basic_form), "status": True}, ensure_ascii=False))

    if request.method == "POST":
        return_form = EditprofileForm_basic(data=request.POST, instance=temp_user)
        status = False
        if return_form.is_valid():
            return_form.save()
            status = True

        return HttpResponse(json.dumps({"status": status, "errors": return_form.errors}, ensure_ascii=False))


@csrf_exempt
def update_profile_password(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    basic_form = EditprofileForm_password()
    if request.method == "GET":
        return HttpResponse(json.dumps({"basic_form": str(basic_form), "status": True}, ensure_ascii=False))

    if request.method == "POST":
        return_form = EditprofileForm_password(data=request.POST)
        status = False
        # print(return_form)
        if return_form.is_valid():
            new_passwd = return_form.clean_passwd_repeat()
            old_passwd = return_form.clean_passwd_old()
            if md5(old_passwd) != temp_user.passwd:
                return_form.add_error("passwd_old", "密码错误")
            else:
                temp_user.passwd = md5(new_passwd)
                temp_user.save()
                status = True
        return HttpResponse(json.dumps({"status": status, "errors": return_form.errors}, ensure_ascii=False))


@csrf_exempt
def update_profile_rights(request):
    userid = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=userid).first()
    rights_form = EditprofileForm_rights()
    current_rights = temp_user.rights
    if request.method == "GET":
        return HttpResponse(json.dumps({"basic_form": str(rights_form), "status": True, "current_rights":current_rights}, ensure_ascii=False))

    if request.method == "POST":
        status = False
        query_dict = request.POST
        right_keys = query_dict["right_keys"]
        description = query_dict["description"]
        rights_string = current_rights
        print(rights_string)
        for i in range(14):
            try:
                temp_string = "right_" + str(i)
                if query_dict[temp_string] == 'on':
                    rights_string = rights_string + ","
                    rights_string = rights_string + str(i)
            except:
                pass
        if rights_string != current_rights:
            status = True
        else:
            if right_keys != []:
                status, rights_string = False, None

        # 生成task，提交给具有审核权限的管理员，审核通过后权限生效
        # if status:
        #     temp_approver = models.UserInfo.objects.filter(type=8).first()
        #     models.Taskinfo.objects.create(task_title=temp_user.username + "申请新的权限", task_type=2, task_status=0,
        #                                    task_description=description, task_applier=temp_user,
        #                                    task_approver=temp_approver, task_create_time=timezone.now(),
        #                                    task_content={"rights_apply": rights_string})
        #     temp_approver.task_todeal += 1
        #     temp_approver.save()
        #     temp_user.task_todeal += 1
        #     temp_user.save()

        # 初始创建全能管理员，只能运行一次！
        if status:
            print('save profile !')
            temp_user.type = 8
            temp_user.rights = "0, 1, 2, 3, 4, 5, 6, 7, 8"
            temp_user.save()
            # temp_approver = models.UserInfo.objects.filter(type=8).first()
            # models.Taskinfo.objects.create(task_title=temp_user.username + "申请新的权限", task_type=2, task_status=0,
            #                                task_description=description, task_applier=temp_user,
            #                                task_approver=temp_approver, task_create_time=timezone.now(),
            #                                task_content={"rights_apply": rights_string})
            # temp_approver.task_todeal += 1
            # temp_approver.save()
            # temp_user.task_todeal += 1
            # temp_user.save()


        return HttpResponse(json.dumps({"status": status}, ensure_ascii=False))


@csrf_exempt
def mainpage(request, userid):
    user_id = request.session["info"]["id"]
    temp_user = models.UserInfo.objects.filter(id=user_id).first()
    return render(request, "mainpage_template.html", {"form": temp_user})