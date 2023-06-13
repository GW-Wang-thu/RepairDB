
def handle_uploaded_file(filepath, f):
    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)