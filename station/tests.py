import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import TrainType, Crew, Train, Route, Station, Journey
from station.serializers import (JourneyListSerializer,
                                 JourneyDetailSerializer)


CREW_URL = reverse("station:crew-list")
JOURNEY_URL = reverse("station:journey-list")


def sample_crew(**params):
    defaults = {
        "first_name": "First",
        "last_name": "Last",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_train(**params):
    train_type = TrainType.objects.create(name="Test type",)
    defaults = {
        "name": "Test train",
        "cargo_num": 10,
        "place_in_cargo": 10,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "K_Test",
        "latitude": 100,
        "longitude": 110
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_route(**params):
    source = Station.objects.create(name="Source",
                                    latitude=100,
                                    longitude=110,
                                    )
    destination = Station.objects.create(name="Destination",
                                         latitude=200,
                                         longitude=110,
                                         )

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 200
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_journey(**params):
    route = sample_route()
    train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2025-10-02 14:00:00",
        "arrival_time": "2025-10-03 14:00:00",
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


def image_crew_upload_url(crew_id):
    return reverse("station:crew-upload-image", args=[crew_id])


def detail_crew_url(crew_id):
    return reverse("station:crew-detail", args=[crew_id])


def image_journey_upload_url(journey_id):
    return reverse("station:journey-upload-image", args=[journey_id])


def detail_journey_url(journey_id):
    return reverse("station:journey-detail", args=[journey_id])


class CrewImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()

    def tearDown(self):
        self.crew.image.delete()

    def test_upload_image_to_crew(self):
        url = image_crew_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.crew.image.path))

    def test_upload_image_to_crew_bad_request(self):
        url = image_crew_upload_url(self.crew.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_crew_list_not_work(self):
        url = CREW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                     "first_name": "Test",
                     "last_name": "Test",
                     "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(first_name="Test")
        self.assertFalse(crew.image)

    def test_image_url_is_shown_on_crew_detail(self):
        url = image_crew_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_crew_url(self.crew.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_crew_list(self):
        url = image_crew_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(CREW_URL)

        self.assertIn("image", res.data["results"][0].keys())


class JourneyImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "password"
        )
        self.client.force_authenticate(self.user)
        crew = sample_crew()
        self.journey = sample_journey()
        self.journey.crew.add(crew)

    def tearDown(self):
        self.journey.image.delete()

    def test_upload_image_to_journey(self):
        url = image_journey_upload_url(self.journey.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.journey.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.journey.image.path))

    def test_upload_image_to_journey_bad_request(self):
        url = image_journey_upload_url(self.journey.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_journey_bad_request(self):
        url = image_journey_upload_url(self.journey.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_journey_list(self):
        url = JOURNEY_URL
        source2 = Station.objects.create(name="Test2",
                                         latitude=200,
                                         longitude=200)
        destination2 = Station.objects.create(name="Kiev",
                                              latitude=300,
                                              longitude=300)
        route = Route.objects.create(source=source2,
                                     destination=destination2,
                                     distance=500)
        train = sample_train(name="100")
        crew = sample_crew()
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "route": route.id,
                    "train": train.id,
                    "departure_time": "2025-10-02 14:00:00",
                    "arrival_time": "2025-10-03 14:00:00",
                    "crew": crew.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        journey = Journey.objects.get(route=route)
        self.assertFalse(journey.image)

    def test_image_url_is_shown_on_journey_detail(self):
        url = image_journey_upload_url(self.journey.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_journey_url(self.journey.id))

        self.assertIn("image", res.data)


class UnauthenticatedJourneyApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        request = self.client.get(JOURNEY_URL)
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_get_journey_list(self):
        sample_journey()
        response = self.client.get(JOURNEY_URL)
        journeys = Journey.objects.all()
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(serializer.data[0].get("route"),
                         response.data.get("results")[0].get("route"))
        self.assertEqual(serializer.data[0].get("id"),
                         response.data.get("results")[0].get("id"))
        self.assertEqual(serializer.data[0].get("train"),
                         response.data.get("results")[0].get("train"))
        self.assertEqual(serializer.data[0].get("departure_time"),
                         response.data.get("results")[0].get("departure_time"))

    def test_search_journey_by_route_date_train(self):
        route1 = sample_route()
        destination = Station.objects.create(
            name="Kiev",
            latitude=100,
            longitude=110
        )
        route2 = Route.objects.create(
            source=Station.objects.create(name="OdTest",
                                          latitude=200,
                                          longitude=200),
            destination=destination,
            distance=400
        )
        route3 = Route.objects.create(
            source=Station.objects.create(name="NkTest",
                                          latitude=400,
                                          longitude=300),
            destination=destination,
            distance=500
        )
        train1 = sample_train(name="100")
        train2 = sample_train(name="200")
        train3 = sample_train(name="300")
        journey1 = Journey.objects.create(
            route=route1,
            train=train1,
            departure_time="2025-10-02 14:00:00",
            arrival_time="2025-10-03 14:00:00",
        )
        journey2 = Journey.objects.create(
            route=route2,
            train=train2,
            departure_time="2025-11-02 14:00:00",
            arrival_time="2025-11-03 14:00:00",
        )
        journey3 = Journey.objects.create(
            route=route3,
            train=train3,
            departure_time="2025-12-02 14:00:00",
            arrival_time="2025-12-03 14:00:00",
        )

        response_by_route = self.client.get(JOURNEY_URL,
                                            {"route": f"{route1.id}"})
        response_by_date = self.client.get(
            JOURNEY_URL,
            {"departure_time": f"{journey2.departure_time.date()}"})
        response_by_train = self.client.get(JOURNEY_URL,
                                            {"train": f"{train3.id}"})

        serializer_1 = JourneyListSerializer(journey1)
        serializer_2 = JourneyListSerializer(journey2)
        serializer_3 = JourneyListSerializer(journey3)

        response_by_route.data.get("results")[0].pop("tickets_available", None)
        response_by_date.data.get("results")[0].pop("tickets_available", None)
        response_by_train.data.get("results")[0].pop("tickets_available", None)

        self.assertEqual(response_by_route.status_code,
                         status.HTTP_200_OK)

        self.assertEqual(serializer_1.data,
                         response_by_route.data.get("results")[0])
        self.assertIn(serializer_2.data,
                      response_by_date.data.get("results"))

        self.assertEqual(serializer_3.data,
                         response_by_train.data.get("results")[0])

    def test_retrieve_journey_detail(self):
        journey = sample_journey()
        crew1 = sample_crew(first_name="Test1", last_name="Test2")
        journey.crew.add(crew1)

        request = self.client.get(detail_journey_url(journey.id))
        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, request.data)

    def test_create_journey_forbidden(self):
        route = sample_route()
        train = sample_train()
        data_journey = {"route": route.id,
                        "train": train.id,
                        "departure_time": "2025-12-02 14:00:00",
                        "arrival_time": "2025-12-03 14:00:00",
                        }
        response = self.client.post(JOURNEY_URL, data_journey)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_journey(self):
        route = sample_route()
        train = sample_train()
        crew = sample_crew()
        data_journey = {"route": route.id,
                        "train": train.id,
                        "departure_time": "2025-12-02 14:00:00",
                        "arrival_time": "2025-12-03 14:00:00",
                        "crew": crew.id,
                        }
        response = self.client.post(JOURNEY_URL, data_journey)
        journey = Journey.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(journey.route.id, data_journey["route"])
        self.assertEqual(journey.train.id, data_journey["train"])
        self.assertEqual(journey.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
                         data_journey["departure_time"])
        self.assertIn(crew, journey.crew.all())

    def test_delete_crew_not_allowed(self):
        crew = sample_crew()

        response = self.client.delete(detail_crew_url(crew.id))
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
