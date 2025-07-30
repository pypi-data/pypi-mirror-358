# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.apps import apps
from django.db.models.base import ModelBase
from xyz_auth.filters import UserResourceFilter
from . import helper
from six import string_types

class RoleResourceFilter(UserResourceFilter):

    # def get_user_scope_map(self, user):
    #     roles = list(user.saas_roles.all())
    #     if not roles:
    #         return
    #     rsm = {}
    #     for r in roles:
    #         rsm.update(r.permissions)
    #     return rsm

    def filter_queryset(self, request, queryset, view):
        # user = request.user
        qset = queryset
        if isinstance(qset, string_types):
            qset = apps.get_model(qset)
        if type(qset) == ModelBase:
            qset = qset.objects.all()
        # scm = helper.get_user_scope_map(user)
        # if scm:
        #     ps = scm.get(qset.model._meta.label_lower)
        #     if ps and ps.get('scope') == '@all':
        #         return qset
        return super(RoleResourceFilter, self).filter_queryset(request, qset, view)
