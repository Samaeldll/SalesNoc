from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.conf import settings

from . import views
from .views import LoginView

urlpatterns = [
    path('contract/', views.contract_new, name='contract_new'),
    path('contract/take/random/', views.contract_take_random, name='contract_take_random'),
    path('contract/archive/', views.contract_archive, name="contract_archive"),
    path('contract/archive/search/', views.ContractArchiveSearch.as_view(), name="ContractArchiveSearch"),
    path('contract/agreements/search', views.ContractSearch.as_view(), name="ContractSearch"),
    path('contract/list/', views.contract_list, name="contract_list"),
    path('contract/list/my/', views.contract_list_my, name="contract_list_my"),
    path('contract/list/my/created', views.contract_list_my, name="contract_list_my_created"),
    path('contract/list/<int:status>/', views.contract_list_by_status, name="contract_list_by_status"),
    path('contract/list/delayed/', views.contract_list_delayed, name="contract_list_delayed"),
    path('contract/list/active/', views.contract_list_active, name="contract_list_active"),

    path('contract/<int:contract_id>/update/internet', views.contract_update_internet, name='contract_update_internet'),
    path('contract/<int:contract_id>/update/television', views.contract_update_television, name='contract_update_television'),
    path('contract/<int:contract_id>/', views.contract_consider, name='contract_consider'),
    path('contract/<int:contract_id>/detail/update/', views.contract_update, name='contract_update'),
    path('contract/<int:contract_id>/detail/', views.contract_detail, name='contract_detail'),
    path('contract/<int:contract_id>/call/', views.contract_call, name='contract_call'),
    path('contract/<int:contract_id>/close/', views.contract_close, name='contract_close'),
    # path('contract/<int:contract_id>/plain/later/', views.contract_plain_later, name='contract_plain_later'),
    path('contract/<int:contract_id>/plain/cancel/', views.contract_plain_cancel, name='contract_plain_cancel'),
    path('contract/<int:contract_id>/assign/', views.contract_assign, name='contract_assign'),
    path('contract/<int:contract_id>/take/', views.contract_take, name='contract_take'),

    path('contract/bulk/status/', views.contract_bulk_status_preview, name='contract_bulk_status_preview'),
    path('contract/bulk/status/apply/', views.contract_bulk_status_apply, name='contract_bulk_status_apply'),

    path('contract/bulk/later/', views.contract_bulk_later_preview, name='contract_bulk_later_preview'),
    path('contract/bulk/later/apply/', views.contract_bulk_later_apply, name='contract_bulk_later_apply'),

    path('contract/statistic/', views.contract_statistic, name='contract_statistic'),
    path('check/address/', views.check_address, name='check_address'),

    path('login/', LoginView.as_view(), name='login'),
    path('permission/', views.permission, name='permission'),
    path('logout/', LogoutView.as_view(next_page="/login"), name='logout')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
