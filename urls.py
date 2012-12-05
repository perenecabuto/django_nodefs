from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',

    url('^tree.json$', 'django_nodefs.views.tree_json'),
    url('^tree.html$', 'django_nodefs.views.tree_widget'),
)
