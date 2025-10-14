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
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return f"{self.name} -cargo_num:{self.cargo_num}, type:{self.train_type}"

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
        return f"{self.name} -latitude:{self.latitude}, longitude:{self.longitude}"



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
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    def __str__(self):
        return (f"{self.route.name} {self.train.name}"
                f"({self.departure_time} - {self.arrival_time})")

    def clean(self):
        if self.departure_time >= self.arrival_time:
            raise ValidationError(
                "Departure time must be earlier than arrival time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Journey, self).save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

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
        return f"{str(self.journey)} (cargo:{self.cargo}), (seat:{self.seat})"
