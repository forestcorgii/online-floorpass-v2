from rest_framework import serializers
from .models import FloorPass, Log, User


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FloorPassSerializer(serializers.ModelSerializer):
    logs = LogSerializer(many=True, read_only=True, source='log_set')
    employees = UserSerializer(many=True, read_only=True, source='user_set')
    # latest_log_date = serializers.CharField(source='owner.latest_log_date')

    class Meta:
        model = FloorPass
        fields = ['id', 'department', 'location', 'status_label',
                  'purpose', 'supervisor_id', 'supervisor_name', 'latest_log_date', 'employees', 'logs']


class ListSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)

# class FloorPassDetailSerializer(serializers.Serializer):
#     id = serializers.CharField()
#     supervisor = serializers.CharField()

# # class FloorPassDetailSerializer(serializers.ModelSerializer):
# #     # id = serializers.CharField()
# #     # supervisor = serializers.CharField()
# #     class Meta:
# #         model = FloorPass
# #         fields = '__all__'
