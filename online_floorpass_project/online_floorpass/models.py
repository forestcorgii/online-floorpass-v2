from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from enum import Enum

from django.db import models
from django.utils import timezone

import datetime
import json


class Department(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_accr = models.CharField(default='', max_length=6)
    objects = models.Manager()


class Location(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_accr = models.CharField(default='', max_length=6)
    departments = models.ManyToManyField(Department)
    objects = models.Manager()


class FloorPass(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department,
                                   on_delete=models.CASCADE,
                                   null=True)
    supervisor_id = models.CharField(max_length=4, blank=True, null=True)
    supervisor_name = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    reference_id = models.CharField(max_length=20, default='')
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def date_created_ph(self):
        return (self.date_created + timedelta(hours=8))

    def reports(self):
        reports = []
        for u in self.user_set.all():
            reports.append({
                'employee': u.employee_id,
                'report': u.report(self)
            })

        return reports


class User(models.Model):
    employee_id = models.CharField(max_length=4, primary_key=True, unique=True)
    employee_name = models.TextField(null=True)

    floorpasses = models.ManyToManyField(FloorPass)

    Status = models.IntegerChoices('Status', 'STAND_BY DEPARTED ARRIVED')
    status = models.IntegerField(choices=Status.choices, default=0, null=True)
    last_modified = models.DateTimeField(auto_now=datetime.datetime.now,
                                         null=True)

    @property
    def last_modified_ph(self):
        return (self.last_modified + timedelta(hours=8))

    @property
    def latest_log_date(self):
        log_count = len(self.log_set.all())
        if log_count == 0:
            return (self.last_modified +
                    timedelta(hours=8)).strftime("%Y-%m-%d %I:%M:%S %p")
        else:
            return self.log_set.all()[log_count - 1].logdatetime_str()

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

    def completed(self):
        return len(self.log_set.all()
                   ) == 0 and self.location == self.current_location(self)

    def report(self, floorpass_id):
        # return [{'dada': 'dada'}]
        destinations = []
        destination = {}
        for l in self.log_set.filter(floorpass=floorpass_id):
            if destination == {}:
                destination['from'] = {'loc': l.location, 'at': l.logdatetime}
                if len(destinations) > 0:
                    prevdes = destinations[-1]
                    p2pelapse = {
                        'from': prevdes['to'],
                        'to': destination['from']
                    }
                    p2pelapse['elapse'] = str(p2pelapse['to']['at'] -
                                              p2pelapse['from']['at']).split(
                                                  '.')[0]
                    destinations.append(p2pelapse)
            else:
                destination['to'] = {'loc': l.location, 'at': l.logdatetime}
                destination['elapse'] = str(destination['to']['at'] -
                                            destination['from']['at']).split(
                                                '.')[0]
                destinations.append(destination)
                destination = {}

        return destinations

    def reports(self, datefrom):
        reports = []
        floorpasses = self.floorpasses.all().order_by('-date_created')
        if datefrom != '':
            floorpasses = self.floorpasses.filter(
                date_created__gte=datefrom).order_by('-date_created')
        for u in floorpasses:
            reports.append({
                'reference_id': u.reference_id,
                'report': self.report(u)
            })

        return reports


class Log(models.Model):
    guard_id = models.CharField(max_length=4, blank=True, null=True)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    logdatetime = models.DateTimeField(auto_now_add=True)
    floorpass = models.ForeignKey(FloorPass, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=True)

    def logdatetime_str(self):
        return (self.logdatetime +
                timedelta(hours=8)).strftime("%Y-%m-%d %I:%M:%S %p")


class GuardManager(models.Model):
    username = models.CharField(max_length=4)
    password = models.CharField(max_length=30)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    mi = models.CharField(max_length=3)

    @property
    def fullname(self):
        return '{} {} {}'.format(self.firstname, self.mi, self.lastname)
