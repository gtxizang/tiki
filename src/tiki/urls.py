from django.urls import path

from .views import api, ui

urlpatterns = [
    path("", ui.home, name="home"),
    path("api/enrich/", api.enrich, name="api-enrich"),
    path("api/result/<uuid:upload_id>/", api.result, name="api-result"),
    path("api/result/<uuid:upload_id>/edit/", api.edit_field, name="api-edit-field"),
    path("health/", api.health, name="health"),
]
