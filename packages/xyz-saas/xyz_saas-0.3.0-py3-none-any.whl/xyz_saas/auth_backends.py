# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


class RolePermissionBackend(object):

    def get_permissions(self, user):
        from .helper import get_user_scope_map
        usm = get_user_scope_map(user)
        if usm:
            from xyz_auth.helper import extract_actions
            from xyz_restful.helper import get_model_actions
            mds = get_model_actions()
            return extract_actions(usm, mds)