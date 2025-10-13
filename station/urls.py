from django.urls import path, include

from rest_framework import routers

from station.views import TrainTypeViewSet, TrainViewSet

app_name = "station"

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)


urlpatterns = [path("", include(router.urls))]
