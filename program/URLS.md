# Program App URLs

The `program` app serves the **تو کجا، من کجا** (Tu Kuja, Man Kuja) event landing page.

## How routing is wired

| Layer | File | Path |
| --- | --- | --- |
| Project | `core/urls.py` | `path('tukuja/', include('program.urls'))` |
| App | `program/urls.py` | `path('', views.tukuja, name='tukuja')` |
| View | `program/views.py` | `tukuja()` → `tukuja/tukuja.html` |

Full public URL:

```text
/tukuja/  +  ''  =  /tukuja/
```

## URL table

| URL | Name | View | Template | Description |
| --- | --- | --- | --- | --- |
| `/tukuja/` | `tukuja` | `program.views.tukuja` | `templates/tukuja/tukuja.html` | EduThanzeel family gathering landing page |

## Reverse in Django

```python
from django.urls import reverse

reverse('tukuja')
# '/tukuja/'
```

```html
<a href="{% url 'tukuja' %}">Tu Kuja, Man Kuja</a>
```

## Local preview

With the development server running:

```text
http://127.0.0.1:8000/tukuja/
```

## Related files

| Role | Path |
| --- | --- |
| URLs | `program/urls.py` |
| Views | `program/views.py` |
| App config | `program/apps.py` (`name = 'program'`) |
| Installed | `core/settings.py` → `INSTALLED_APPS` includes `'program'` |
| Template | `templates/tukuja/tukuja.html` |
| Static | `static/tukuja/` |

## Adding more program pages

Add a view in `program/views.py`, then a route in `program/urls.py`. Because the app is included at `tukuja/`, a new path is appended to that prefix.

```python
# program/urls.py
urlpatterns = [
    path('', views.tukuja, name='tukuja'),
    path('about/', views.tukuja_about, name='tukuja_about'),  # → /tukuja/about/
]
```
