from rest_framework import generics
from rest_framework.decorators import api_view

from . import models
from . import serializers
from django.http import JsonResponse, HttpResponse

from rest_framework.response import Response
from rest_framework.reverse import reverse

from datetime import datetime, timedelta
from django.utils import timezone
import pytz


@api_view(['POST'])
def guardLogin(request):
    if request.method == 'POST':
        guard = models.GuardManager.objects.filter(
            username=request.POST['username'],
            password=request.POST['password'])
        if len(guard) > 0:
            serializer = serializers.Guard(guard[0])
            # if serializer.is_valid():
            return Response(serializer.data)
            # return Response(serializer.errors)
        return Response({'response': 'invalid username or password'})


@api_view(['GET'])
def filter(request):
    if request.method == 'GET':
        floorpass = models.FloorPass.objects.all()

        if request.GET.get('username', False) or request.GET['username'] != '':
            floorpass = floorpass.filter(
                user__employee_id__contains=request.GET['username'])
        # else:
        if request.GET.get('department',
                           False) or request.GET['department'] != '':
            floorpass = floorpass.filter(
                department=models.Department.objects.filter(
                    name__iexact=request.GET['department'])[0].name)
        if request.GET.get('location', False) or request.GET['location'] != '':
            floorpass = floorpass.filter(
                location=models.Location.objects.filter(
                    name__iexact=request.GET['location'])[0].name)

        if request.GET.get('sort', False):
            if 'latest_log_date' in request.GET['sort']:
                floorpass = sorted(floorpass,
                                   key=lambda f: f.latest_log_date,
                                   reverse='-' in request.GET['sort'])

        logCount = len(floorpass)
        limitPerPage = 1
        maxPageCount = 1
        if request.GET.get('limit', False) and len(floorpass) != 0:
            pageCount = int(request.GET['page'])
            limitPerPage = int(request.GET['limit'])
            i_range_start = (pageCount - 1) * limitPerPage
            i_range_end = i_range_start + limitPerPage
            if i_range_end >= len(floorpass):
                i_range_end = len(floorpass)
            floorpass = floorpass[i_range_start:i_range_end]

        if logCount > 0:
            maxPageCount = (logCount // limitPerPage) + (
                1 if (logCount % limitPerPage) >= 1 else 0)

        serializer = serializers.FloorPass(floorpass, many=True)
        return Response({
            'maxPageCount': maxPageCount,
            'logCount': logCount,
            'logs': serializer.data
        })


@api_view(['GET'])
def list(request):
    if request.method == 'GET':
        if request.GET.get('type', False):
            _list = None
            if request.GET['type'] == 'department':
                _list = models.Department.objects.all()
            elif request.GET['type'] == 'location':
                _list = models.Location.objects.all()
                listArr = []
                for i in _list:
                    item = {'name': i.name}
                    departments = []
                    for j in i.departments.all():
                        departments.append({'name': j.name})
                    item['departments'] = departments
                    listArr.append(item)

            # serializer = ListSerializer(_list, many=True)
            return Response(listArr)


@api_view(['POST'])
def writeNewFloorpass(request):
    if request.method == 'POST':
        department = models.Department.objects.get(
            name__iexact=request.POST['department'])
        location = models.Location.objects.get(
            name__iexact=request.POST['location'])
        floorpass = models.FloorPass(
            supervisor_id=request.POST['supervisor_id'],
            supervisor_name=request.POST['supervisor_name'],
            department=department,
            location=location,
            purpose=request.POST['purpose'],
            status=0,
            reference_id="{}{}{:06d}".format(
                location.name_accr, department.name_accr,
                len(
                    models.FloorPass.objects.filter(department=department,
                                                    location=location))))
        floorpass.save()

        for i in request.POST['employees'].split(';'):
            if i != '':
                userinf = i.split('|')
                user = models.User(floorpass=floorpass,
                                   employee_id=userinf[0],
                                   employee_name=userinf[1]).save()
        return Response({'Response': 'may napala'})


@api_view(['POST', 'DELETE'])
def writeFloorpass(request, floorpass_id):
    if request.method == 'POST':
        floorpass = models.FloorPass.objects.filter(pk=floorpass_id)
        floorpass.update(
            department=models.Department.objects.get(
                name__iexact=request.POST['department']),
            location=models.Location.objects.get(
                name__iexact=request.POST['location']),
            purpose=request.POST['purpose'],
        )
        floorpass[0].user_set.all().delete()

        for i in request.POST['employees'].split(';'):
            if i != '':
                userinf = i.split('|')
                user = models.User(floorpass=floorpass[0],
                                   employee_id=userinf[0],
                                   employee_name=userinf[1]).save()
        return Response({'Response': request.POST['employees'].split(';')})
    elif request.method == 'DELETE':
        models.FloorPass.objects.filter(pk=floorpass_id)
        return Response({'Response': 'Deleted ' + floorpass_id})


@api_view(['GET'])
def checkNewLog(request):
    if request.method == 'GET':
        floorpass = models.FloorPass.objects.all()

        if request.GET.get('department',
                           False) or request.GET['department'] != '':
            floorpass = floorpass.filter(
                department=models.Department.objects.filter(
                    name__iexact=request.GET['department'])[0].name)
        if request.GET.get('location', False) or request.GET['location'] != '':
            floorpass = floorpass.filter(
                location=models.Location.objects.filter(
                    name__iexact=request.GET['location'])[0].name)

        filtered = [
            x for x in floorpass
            if x.latest_log_date > request.GET['latest_log_date']
        ]

        return Response({'new_logs_count': len(filtered)})


class FloorPassList(generics.ListCreateAPIView):
    queryset = models.FloorPass.objects.all()
    serializer_class = serializers.FloorPass


class FloorPassDetail(generics.RetrieveUpdateAPIView):
    queryset = models.FloorPass.objects.all()
    serializer_class = serializers.FloorPass


class LogList(generics.ListCreateAPIView):
    queryset = models.Log.objects.all()
    serializer_class = serializers.Log


@api_view(['POST'])
def writeLog(request):
    if request.method == 'POST':
        floorpass = [
            x for x in models.FloorPass.objects.all()
            if x.reference_id == request.POST['floorpass']
        ]
        if floorpass != None and len(floorpass) > 0:
            floorpass = floorpass[0]
            log = models.Log(guard_id=request.POST['guard_id'],
                             floorpass=floorpass,
                             location=request.POST['location'])
            log.save()

            if len(floorpass.log_set.all(
            )) > 1 and floorpass.location.name == request.POST['location']:
                models.FloorPass.objects.filter(pk=floorpass.id).update(
                    status=2)
            else:
                models.FloorPass.objects.filter(pk=floorpass.id).update(
                    status=1)
            return Response({'Response': len(floorpass.log_set.all())})
        else:
            return Response({'Response': floorpass[0].reference_id})


@api_view(['GET'])
def findLog(request):
    if request.method == 'GET':
        floorpass = models.FloorPass.objects.filter(
            user__employee_id__iexact=request.GET['id']).order_by(
                '-last_modified')
        if floorpass != None and floorpass.count() > 0:
            serializer = serializers.FloorPass(floorpass[0])
            # if serializer.is_valid():
            if (datetime.today().replace(tzinfo=pytz.UTC) - timedelta(hours=11)
                ) < floorpass[0].last_modified_ph.replace(tzinfo=pytz.UTC):
                return Response(serializer.data)
            return Response({
                'Response': 'Too Late!!',
                'date found': floorpass[0].last_modified_ph,
                'date now': timezone.now(),
                'Result': serializer.data
            })
        else:
            return Response({'Response': request.GET['id']})


class LogDetail(generics.RetrieveUpdateAPIView):
    queryset = models.Log.objects.all()
    serializer_class = serializers.Log


class UserList(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.User
    lookup_fields = ['employee_id']


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.User
