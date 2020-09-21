from rest_framework import generics
from rest_framework.decorators import api_view

from .models import FloorPass, User, Log,  Department, Location
from .serializers import FloorPassSerializer, LogSerializer, UserSerializer, ListSerializer
from django.http import JsonResponse, HttpResponse

from rest_framework.response import Response
from rest_framework.reverse import reverse

# @api_view(['GET', 'POST'])
# def ReferenceID(request):
#     if request.method == 'GET':
#         floorpass = FloorPass.objects.get(pk=request.GET['id'])
#         serializer = FloorPassDetailSerializer(floorpass)
#         return JsonResponse(serializer.data)
#     elif request.method == 'POST':
#         floorpass = FloorPass.objects.get(pk=request.GET['id'])


@api_view(['GET'])
def filter(request):
    if request.method == 'GET':
        floorpass = FloorPass.objects.all()

        if request.GET.get('username', False) or request.GET['username'] !='':
            floorpass = floorpass.filter(
                supervisor_id__iexact=request.GET['username'])
        # else:
        if request.GET.get('department', False) or request.GET['department'] !='':
            floorpass = floorpass.filter(
                    department=Department.objects.filter(name__iexact=request.GET['department'])[0].name)
        if request.GET.get('location', False) or request.GET['location'] != '':
            floorpass = floorpass.filter(location=Location.objects.filter(name__iexact=request.GET['location'])[0].name)

        if request.GET.get('sort', False):
            if 'latest_log_date' in request.GET['sort']:
                floorpass = sorted(
                    floorpass, key=lambda f: f.latest_log_date, reverse='-'in request.GET['sort'])
            
        logCount = len(floorpass)
        limitPerPage = 1
        maxPageCount = 1  
        if request.GET.get('limit', False) and len(floorpass) != 0:
            pageCount = int(request.GET['page'])
            limitPerPage = int(request.GET['limit'])
            i_range_start = (pageCount-1) * limitPerPage
            i_range_end = i_range_start + limitPerPage
            if i_range_end >= len(floorpass):
                i_range_end = len(floorpass)
            floorpass = floorpass[i_range_start:i_range_end]
        
        if logCount > 0:
            maxPageCount = (logCount // limitPerPage) + ( 1 if (logCount % limitPerPage) >= 1 else 0)

            
        serializer = FloorPassSerializer(floorpass, many=True)
        return Response({'maxPageCount':maxPageCount,'logCount': logCount,'logs':serializer.data} )


@api_view(['GET'])
def list(request):
    if request.method == 'GET':
        if request.GET.get('type', False):
            _list = None
            if request.GET['type'] == 'department':
                _list = Department.objects.all()
            elif request.GET['type'] == 'location':
                _list = Location.objects.all()
                listArr = []
                for i in _list:
                    item = {'name': i.name}
                    departments=[]
                    for j in i.departments.all():
                        departments.append({'name':j.name})
                    item['departments']=departments
                    listArr.append(item)

            # serializer = ListSerializer(_list, many=True)
            return Response(listArr)


@api_view(['POST'])
def writeNewFloorpass(request):
    if request.method == 'POST':
        floorpass = FloorPass(
         supervisor_id=request.POST['supervisor_id'],
         supervisor_name=request.POST['supervisor_name'],
         department=Department.objects.get(name__iexact=request.POST['department']),
         location=Location.objects.get(name__iexact=request.POST['location']),
         purpose=request.POST['purpose'],
         status=0
        )
        floorpass.save()
            
        for i in request.POST['employees'].split(';'):
            if i != '':
                userinf=i.split('|')
                user = User(floorpass=floorpass,employee_id=userinf[0],employee_name=userinf[1]).save()
        return Response({'Response': 'may napala'})
        
@api_view(['POST'])
def writeFloorpass(request,floorpass_id):
    if request.method == 'POST':
        floorpass = FloorPass.objects.filter(pk=floorpass_id)
        floorpass.update(
         department=Department.objects.get(name__iexact=request.POST['department']),
         location=Location.objects.get(name__iexact=request.POST['location']),
         purpose=request.POST['purpose'],
         )
        floorpass[0].user_set.all().delete()
            
        for i in request.POST['employees'].split(';'):
            if i != '':
                userinf=i.split('|')
                user = User(floorpass=floorpass[0],employee_id=userinf[0],employee_name=userinf[1]).save()
        return Response({'Response':request.POST['employees'].split(';')})

@api_view(['GET'])
def checkNewLog(request):
    if request.method == 'GET':
        floorpass = FloorPass.objects.all() 
        if request.GET.get('username', False) or request.GET['username'] !='':
            floorpass = floorpass.filter(
                supervisor_id__iexact=request.GET['username'])
        # else:
        if request.GET.get('department', False) or request.GET['department'] !='':
            floorpass = floorpass.filter(
                    department=Department.objects.filter(name__iexact=request.GET['department'])[0].name)
        if request.GET.get('location', False) or request.GET['location'] != '':
            floorpass = floorpass.filter(location=Location.objects.filter(name__iexact=request.GET['location'])[0].name)

        filtered = [x for x in floorpass if x.latest_log_date > request.GET['latest_log_date']]

        # serializer = FloorPassSerializer(filtered, many=True)
        # return Response({'new_log_count': len(filtered),'logs':serializer.data} )
        return Response({'new_logs_count':len(filtered)})


class FloorPassList(generics.ListCreateAPIView):
    queryset = FloorPass.objects.all()
    serializer_class = FloorPassSerializer




class FloorPassDetail(generics.RetrieveUpdateAPIView):
    queryset = FloorPass.objects.all()
    serializer_class = FloorPassSerializer


class LogList(generics.ListCreateAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

@api_view(['POST'])
def writeLog(request):
    if request.method == 'POST':
        floorpass = FloorPass.objects.get(pk=request.POST['floorpass']
        # department=Department.objects.filter(name__iexact=request.GET['department'])[0].name
        # location=Location.objects.filter(name__iexact=request.GET['location'])[0].name
        )
        log = Log(guard_id=request.POST['guard_id'], floorpass=floorpass, location=request.POST['location'])
        log.save()

        if len(floorpass.log_set.all()) > 1 and floorpass.location.name == request.POST['location']:
            FloorPass.objects.filter(pk=floorpass.id).update(status=2)
        else:
            FloorPass.objects.filter(pk=floorpass.id).update(status=1)
        return Response({'Response': 'may napala'})

class LogDetail(generics.RetrieveUpdateAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_fields = ['employee_id']


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
