# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from tenant_schemas import middleware as M


class TenantMiddleware(M.TenantMiddleware):

    def hostname_from_request(self, request):
        return request.META.get('TENANT_SUBDOMAIN','').lower()
