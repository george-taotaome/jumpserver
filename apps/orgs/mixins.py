# -*- coding: utf-8 -*-
#
from django.db import models
from django.shortcuts import redirect
import warnings
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from common.utils import get_logger
from .utils import get_current_org, set_current_org

logger = get_logger(__file__)


__all__ = [
    'OrgManager', 'OrgViewGenericMixin', 'OrgModelMixin', 'OrgModelForm'
]


class OrgManager(models.Manager):
    def get_queryset(self):
        current_org = get_current_org()
        kwargs = {}

        print(">>>>>>>>>> Get query set")
        if not current_org:
            kwargs['id'] = None
        elif current_org.is_real():
            kwargs['org'] = current_org
        elif current_org.is_default():
            kwargs['org'] = None
        queryset = super(OrgManager, self).get_queryset()
        queryset = queryset.filter(**kwargs)
        # print(kwargs)
        print(queryset.query)
        return queryset

    def all(self):
        current_org = get_current_org()
        if not current_org:
            msg = 'You can `objects.set_current_org(org).all()` then run it'
            warnings.warn(msg)
            return self
        else:
            return super(OrgManager, self).all()

    def set_current_org(self, org):
        set_current_org(org)
        return self


class OrgModelMixin(models.Model):
    org = models.ForeignKey('orgs.Organization', on_delete=models.PROTECT, null=True)
    objects = OrgManager()

    def save(self, *args, **kwargs):
        current_org = get_current_org()
        if current_org and current_org.is_real():
            self.org = current_org
        return super(OrgModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class OrgViewGenericMixin:
    def dispatch(self, request, *args, **kwargs):
        current_org = get_current_org()
        if not current_org:
            return redirect('orgs:switch-a-org')
        return super().dispatch(request, *args, **kwargs)


class OrgModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' not in kwargs:
            return
        for name, field in self.fields.items():
            if not hasattr(field, 'queryset'):
                continue
            print(field)
            model = field.queryset.model
            field.queryset = model.objects.all()
