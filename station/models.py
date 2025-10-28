from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cargo_num = models.IntegerField()
    place_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType,
                                   on_delete=models.CASCADE,
                                   related_name="trains")

    def __str__(self):
        return (f"{self.name} "
                f"-cargo_num: {self.cargo_num}, "
                f"type: {self.train_type}")

    class Meta:
        verbose_name_plural = "trains"
        ordering = ["name"]


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        verbose_name_plural = "stations"

    def __str__(self):
        return (f"{self.name} "
                f"-latitude: {self.latitude}, "
                f" longitude: {self.longitude}")


class Route(models.Model):
    source = models.ForeignKey(Station,
                               on_delete=models.CASCADE,
                               related_name="routes_source")
    destination = models.ForeignKey(Station,
                                    on_delete=models.CASCADE,
                                    related_name="routes_destination")
    distance = models.IntegerField()

    @property
    def name(self):
        return f"{self.source.name}-{self.destination.name}"

    class Meta:
        verbose_name_plural = "routes"
        unique_together = ["source", "destination"]
        ordering = ("source", "destination", "distance")

    def __str__(self):
        return f"{self.name}, distance: {self.distance} km"


class Journey(models.Model):
    route = models.ForeignKey(Route,
                              on_delete=models.CASCADE,
                              related_name="journeys")
    train = models.ForeignKey(Train,
                              on_delete=models.CASCADE,
                              related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    def __str__(self):
        return (f"{self.route.name} {self.train.name}"
                f"({self.departure_time} - {self.arrival_time})")

    @staticmethod
    def validate_departure_time(departure_time, arrival_time, error_to_raise):
        if departure_time >= arrival_time:
            raise error_to_raise(
                "Departure time must be earlier than arrival time.")

    def clean(self):
        Journey.validate_departure_time(
            self.departure_time,
            self.arrival_time,
            ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Journey, self).save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey,
                                on_delete=models.CASCADE,
                                related_name="tickets")
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="tickets")

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]

    def __str__(self):
        return (f"{str(self.journey)} "
                f"(cargo: {self.cargo}), "
                f"(seat: {self.seat})")

    @staticmethod
    def validate_ticket(cargo, seat, journey, error_to_raise):
        if not 1 <= cargo <= journey.train.cargo_num:
            raise error_to_raise(
                f"Cargo must be between 1 and {journey.train.cargo_num}")
        if not 1 <= seat <= journey.train.cargo_num:
            raise error_to_raise(
                f"Seat must be between 1 and {journey.train.cargo_num}")

    def clean(self):
        Ticket.validate_ticket(self.cargo,
                               self.seat,
                               self.journey,
                               ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)
