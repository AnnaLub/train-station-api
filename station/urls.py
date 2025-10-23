from django.urls import path, include

from rest_framework import routers

from station.views import TrainTypeViewSet, TrainViewSet, CrewViewSet, StationViewSet, RouteViewSet, JourneyViewSet

app_name = "station"

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("crews", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("journey", JourneyViewSet)

urlpatterns = [path("", include(router.urls))]
