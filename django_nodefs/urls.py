from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'django_nodefs.views',

    url('^tree.json$', 'tree_json'),
    url('^tree.html$', 'tree_widget'),
)
