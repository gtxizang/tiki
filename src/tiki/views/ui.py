from django.shortcuts import render


def home(request):
    """Render the upload page."""
    return render(request, "tiki/home.html")
