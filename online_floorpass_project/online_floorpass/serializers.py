from rest_framework import serializers
from . import models


class Log(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ['id','guard_id','logdatetime_str','location','floorpass']


class User(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class FloorPass(serializers.ModelSerializer):
    logs = Log(many=True, read_only=True, source='log_set')
    employees = User(many=True, read_only=True, source='user_set')
    # latest_log_date = serializers.CharField(source='owner.latest_log_date')

    class Meta:
        model = models.FloorPass
        fields = ['id','reference_id', 'department', 'location', 'status_label',
                  'purpose', 'supervisor_id', 'supervisor_name', 'latest_log_date', 'employees', 'logs']


class List(serializers.Serializer):
    name = serializers.CharField(read_only=True)


class Guard(serializers.ModelSerializer):
    class Meta:
        model = models.GuardManager
        fields = ['username','fullname']

# class FloorPassDetailSerializer(serializers.Serializer):
#     id = serializers.CharField()
#     supervisor = serializers.CharField()

# # class FloorPassDetailSerializer(serializers.ModelSerializer):
# #     # id = serializers.CharField()
# #     # supervisor = serializers.CharField()
# #     class Meta:
# #         model = FloorPass
# #         fields = '__all__'
