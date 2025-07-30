# -*- coding:utf-8 -*-

from . import models, serializers, signals

from rest_framework import viewsets, decorators, response
from xyz_restful.decorators import register

__author__ = 'denishuang'


@register()
class PartyViewSet(viewsets.ModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer

    def get_permissions(self):
        party = self.queryset.first()
        if not party:
            return []
        return super(PartyViewSet, self).get_permissions()

    # @decorators.action(['GET'], detail=False, permission_classes=[])
    # def current(self, request):
    #     party = models.Party.objects.first()
    #     data = self.get_serializer(party).data
    #     return response.Response(data)

    @decorators.action(['GET'], detail=False, permission_classes=[])
    def current(self, request):
        party = models.Party.objects.first()
        srs = signals.to_get_party_settings.send(sender=self, party=party, request=request)
        data = self.get_serializer(party).data
        ds = data['settings'] or {}
        for func, rs in srs:
            ds.update(rs)
        data['settings'] = ds
        return response.Response(data)
