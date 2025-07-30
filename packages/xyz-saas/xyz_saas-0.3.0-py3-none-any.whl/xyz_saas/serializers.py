# -*- coding:utf-8 -*-

__author__ = 'denishuang'
from . import models
from rest_framework import serializers
from xyz_restful.mixins import IDAndStrFieldSerializerMixin
class PartySerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Party
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time')


class RoleNameSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = ('name',)
