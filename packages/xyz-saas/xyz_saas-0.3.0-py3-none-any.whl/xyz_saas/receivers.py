# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models.signals import post_save
from xyz_auth.signals import to_get_role_model_map, to_get_user_roles, to_get_user_profile
from .signals import to_get_party_settings
from . import models, serializers

# @receiver(post_save, sender=models.Party)
# def create_tenant(sender, **kwargs):
#     if kwargs['created']:
#         party = kwargs['instance']
#         from xyz_tenant.tasks import gen_tenant
#         data = dict(schema_name=party.uid, domain_url=party.slug, name=party.name)
#         gen_tenant.delay(data)



# @receiver(to_get_party_settings)
# def get_party_settings(sender, **kwargs):
#     p = models.Party.objects.first()
#     return {'saas': {'party': p.settings}}

@receiver(to_get_role_model_map)
def get_role_model_map(sender, **kwargs):
    from .helper import get_role_model_map
    return get_role_model_map()


@receiver(to_get_user_roles)
def get_user_roles(sender, **kwargs):
    user = kwargs['user']
    rns = getattr(user, '_user_role_names', None)
    if rns is None:
        rns = list(user.saas_roles.all().values_list('name', flat=True))
        setattr(user, '_user_role_names', rns)
        # print('to_get_user_roles', user.id)
    return rns

@receiver(to_get_user_profile)
def get_current_user_roles(sender, **kwargs):
    user = kwargs['user']
    qset = user.saas_roles.all()
    return serializers.RoleNameSerializer(qset, many=True)