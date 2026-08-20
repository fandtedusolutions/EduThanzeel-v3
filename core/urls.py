from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve as static_serve


urlpatterns = [
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=f'{settings.STATIC_URL}admission/images/favicon.ico',
            permanent=True,
        ),
    ),
    path('admin/', admin.site.urls),
    path('', include('admissions.urls')),
    path('tukuja/', include('program.urls')),
]

# Custom error pages
handler400 = 'admissions.views.custom_400'
handler403 = 'admissions.views.custom_403'
handler404 = 'admissions.views.custom_404'
handler500 = 'admissions.views.custom_500'

# Serve static/media when DEBUG=False (or alongside runserver).
#
# Serving only STATICFILES_DIRS misses Django admin CSS/JS — those live under
# django/contrib/admin/static/, not in your project `static/` folder.
# staticfiles.views.serve uses finders so /static/admin/... resolves correctly.
#
# insecure=True is required when DEBUG=False (dev only; use Nginx/Whitenoise in production).
_static_prefix = settings.STATIC_URL.strip("/")
urlpatterns += [
    re_path(
        rf"^{_static_prefix}/(?P<path>.*)$",
        staticfiles_serve,
        kwargs={"insecure": not settings.DEBUG},
    ),
    path(
        f"{settings.MEDIA_URL.lstrip('/')}<path:path>",
        static_serve,
        {"document_root": str(settings.MEDIA_ROOT)},
    ),
]