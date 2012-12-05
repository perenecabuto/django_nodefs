from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',

    url('^contas_tree.json$', 'django_nodefs.views.tree_json'),
    url('^contas_tree.html$', 'django_nodefs.views.tree_widget'),
)
