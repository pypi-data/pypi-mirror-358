from django.apps import apps
from django.contrib.auth import authenticate, login, logout, mixins
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


def health_check(request):
    return HttpResponse('Service is running!')


class ListInstalledHuscyAppsView(mixins.LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        app_names = [app.name
                     for app in apps.get_app_configs()
                     if hasattr(app, 'HuscyAppMeta')]
        return Response(sorted(app_names), status=HTTP_200_OK)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if user is None:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)
        return Response({'message': _('Login successful')}, status=HTTP_200_OK)


class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': _('Success')}, status=HTTP_200_OK)
