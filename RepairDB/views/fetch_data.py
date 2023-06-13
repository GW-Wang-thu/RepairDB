

def fetch_picture(request, picname):
    print("Fetch: " + picname)

    # DetailView默认Context_object_name是picture

    # 下面是DetailView默认模板，可以换成自己的
    # template_name = 'pic_upload/picture_detail.html'