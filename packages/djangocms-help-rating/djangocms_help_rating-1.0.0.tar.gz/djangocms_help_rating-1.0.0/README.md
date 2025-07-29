# DjangoCMS Help Rating

A project for simple evaluation of [DjangoCMS](https://www.django-cms.org/) website content.

### Install

`pip install djangocms-help-rating`


Add into settings.py:

```python
INSTALLED_APPS = [
    ...
    "help_rating",
]
```

Add into site urls.py:

```python
urlpatterns = [
    ...
    path('help-rating/', include(('help_rating.urls', "help_rating"))),
]
```

If you define a namespace other than ``help_rating`` in the urls.py, you must redefine it in settings with the value ``HELP_RATING_PATH_NAMESPACE``.
Default of ``HELP_RATING_PATH_NAMESPACE`` is `"help_rating"`.

### License

BSD License
