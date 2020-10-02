from rest_framework import serializers
from . import models


class Log(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = '__all__'


class User(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class FloorPass(serializers.ModelSerializer):
    employees = User(many=True, read_only=True, source='user_set')

    # latest_log_date = serializers.CharField(source='owner.latest_log_date')

    class Meta:
        model = models.FloorPass
        fields = [
            'id', 'reference_id', 'department', 'location', 'purpose',
            'supervisor_id', 'employees', 'reports'
        ]


class LogStrip(serializers.ModelSerializer):
    floorpass_id = serializers.CharField(read_only=True,
                                         source='floorpass.id',
                                         default='')
    employee_id = serializers.CharField(read_only=True,
                                        source='employee.employee_id',
                                        default='')
    reference_id = serializers.CharField(read_only=True,
                                         source='floorpass.reference_id')
    supervisor_id = serializers.CharField(read_only=True,
                                          source='floorpass.supervisor_id')
    department = serializers.CharField(read_only=True,
                                       source='floorpass.department.name')
    location = serializers.CharField(read_only=True,
                                     source='floorpass.location.name')
    purpose = serializers.CharField(read_only=True, source='floorpass.purpose')
    status = serializers.CharField(read_only=True,
                                   source='employee.status_label')

    class Meta:
        model = models.Log
        fields = [
            'employee_id', 'supervisor_id', 'floorpass_id', 'reference_id',
            'department', 'location', 'purpose', 'status', 'logdatetime_str'
        ]


class List(serializers.Serializer):
    name = serializers.CharField(read_only=True)


class Guard(serializers.ModelSerializer):
    class Meta:
        model = models.GuardManager
        fields = ['username', 'fullname']


# class FloorPassDetailSerializer(serializers.Serializer):
#     id = serializers.CharField()
#     supervisor = serializers.CharField()

# # class FloorPassDetailSerializer(serializers.ModelSerializer):
# #     # id = serializers.CharField()
# #     # supervisor = serializers.CharField()
# #     class Meta:
# #         model = FloorPass
# #         fields = '__all__'
