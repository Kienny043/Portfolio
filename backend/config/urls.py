from django.urls import include, path, re_path

from core.views import spa_index

urlpatterns = [
    path("api/", include("core.urls")),
    # Everything else that isn't an /api/ route (and wasn't a static file) gets the React app.
    re_path(r"^(?!api(?:/|$))(?P<path>.*)$", spa_index),
]
