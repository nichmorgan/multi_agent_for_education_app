from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
import os
from ingest.tasks import process_upload


def upload_file(request):
    if request.method == "POST" and request.FILES["file"]:
        myfile = request.FILES["file"]
        fs = FileSystemStorage(location="media/uploads")
        filename = fs.save(myfile.name, myfile)
        uploaded_file_path = fs.path(filename)

        # Enqueue the processing task
        try:
            process_upload(uploaded_file_path)
            messages.success(
                request, f"File loaded successfully. Processing started for {filename}."
            )
        except Exception as e:
            messages.error(request, f"Error starting process: {e}")

        return redirect("upload_file")

    return render(request, "ingest/upload.html")
