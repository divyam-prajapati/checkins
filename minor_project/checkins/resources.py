from import_export import resources
from .models import *

class EventResource(resources.ModelResource):
    class Meta:
        model = Event

class InvitesResource(resources.ModelResource):
    class Meta:
        model = Invites

class CheckinsResource(resources.ModelResource):
    class Meta:
        model = Checkins