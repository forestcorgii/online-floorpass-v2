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
                    floorpass, key=lambda f: f.latest_log_date)  # , reverse='-'in request.GET['sort'])
            # floorpass = floorpass.order_by(request.GET['sort'])

        if request.GET.get('limit', False):
            floorpass = floorpass[:int(request.GET['limit'])]

        serializer = FloorPassSerializer(floorpass, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def list(request):
    if request.method == 'GET':
        if request.GET.get('type', False):
            _list = None
            if request.GET['type'] == 'department':
                _list = Department.objects.all()
            elif request.GET['type'] == 'location':
                _list = Location.objects.all()

            serializer = ListSerializer(_list, many=True)
            return JsonResponse(serializer.data, safe=False)


# @api_view(['DELETE'])
# def delete(request):
#     if request.method == 'DELETE':
#         user = User.objects.filter(floorpass=)


class FloorPassList(generics.ListCreateAPIView):
    queryset = FloorPass.objects.all()
    serializer_class = FloorPassSerializer


class FloorPassDetail(generics.RetrieveUpdateAPIView):
    queryset = FloorPass.objects.all()
    serializer_class = FloorPassSerializer


class LogList(generics.ListCreateAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer


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
