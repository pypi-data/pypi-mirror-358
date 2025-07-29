import json
from django import template
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()

@register.filter
def dumpjson(value):
    return json.dumps(value, cls=DjangoJSONEncoder)
