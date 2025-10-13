from django.contrib import admin

from station.models import TrainType, Train

admin.site.register(TrainType)
admin.site.register(Train)