from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from enum import Enum

from django.db import models
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    objects = models.Manager()


class Department(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    objects = models.Manager()


class FloorPass(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True)
    supervisor_id = models.CharField(max_length=4, blank=True, null=True)
    supervisor_name = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    Status = models.IntegerChoices('Status', 'STAND_BY DEPARTED ARRIVED')
    status = models.IntegerField(choices=Status.choices, null=True)
    # latest_log_date = models.DateTimeField(blank=True, null=True)
    objects = models.Manager()

    @property
    def latest_log_date(self):
        log_count = len(self.log_set.all())
        if log_count == 0:
            return timezone.now().strftime("%m-%d %H:%M:%S")
        else:
            return self.log_set.all()[log_count - 1].logdatetime_str

    def status_label(self):
        if self.status is None:
            return ''
        else:
            return self.Status.choices[self.status][1]

    def current_location(self):
        if len(self.log_set.all()) == 0:
            return self.location.name
        else:
            return self.log_set.order_by('logdatetime')[0].location

    def timein(self):
        if len(self.log_set.all()) == 0:
            return ''
        else:
            return self.log_set.all()[0].logdatetime_str

    def timeout(self):
        log_count = len(self.log_set.all())
        if log_count <= 1:
            return ''
        elif log_count > 1 and self.location.name == self.log_set.all()[log_count - 1].location:
            return self.log_set.all()[log_count - 1].logdatetime_str

    def time_elapse(self):
        log_count = len(self.log_set.all())
        if log_count <= 1:
            return ''
        else:
            return str(self.log_set.all()[log_count - 1].logdatetime - self.log_set.all()[0].logdatetime).split(".")[0]

    def completed(self):
        return len(self.log_set.all()) == 0 and self.location == self.current_location(self)


class Log(models.Model):
    guard_id = models.CharField(max_length=4, blank=True, null=True)
    logdatetime = models.DateTimeField(auto_now_add=True)
    floorpass = models.ForeignKey(FloorPass, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=True)

    @property
    def logdatetime_str(self):
        return self.logdatetime.strftime("%Y-%m-%d %H:%M:%S")



class User(models.Model):
    floorpass = models.ForeignKey(FloorPass, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=4, null=True)
    employee_name = models.TextField(null=True)

    def duplicate(self):
        return not self.objects.filter(Location, pk=self.employee_id) is None
