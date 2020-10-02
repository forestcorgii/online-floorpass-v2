from django.urls import path, include, re_path
from . import views
from . import api

from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'floorpass'

urlpatterns = format_suffix_patterns([
    re_path('^filter/$', api.filter),
    path('', api.filter),
    re_path('^list/$', api.list),
    path('floorpass/', api.FloorPassList.as_view(), name='floorpass-list'),
    path('floorpass/<int:pk>/', api.FloorPassDetail.as_view()),
    #      name='floorpass-detail'),
    path('guardlogin/', api.guardLogin),
    path('findlog/', api.findLog),
    path('check_log/', api.checkNewLog),
    path('floorpass/', api.writeNewFloorpass),
    # path('floorpass/<int:floorpass_id>/',api.writeFloorpass),
    path('log/', api.writeLog, name='log-create'),
    # path('log/<int:pk>/', api.LogDetail.as_view(), name='log-detail'),
    # path('user/', api.UserList.as_view(), name='user-list'),
    # path('user/<int:pk>/', api.UserDetail.as_view(), name='user-detail'),
])
