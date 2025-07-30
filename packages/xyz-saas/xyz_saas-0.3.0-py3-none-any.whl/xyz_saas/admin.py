# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from . import models


@admin.register(models.Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo')


@admin.register(models.Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', )
    raw_id_fields = ('user', )


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', )
    raw_id_fields = ('users',)
