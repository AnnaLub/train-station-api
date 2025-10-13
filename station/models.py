from django.db import models


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField()
    place_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return f"{self.name} -cargo_num:{self.cargo_num}, type:{self.train_type}"

    class Meta:
        verbose_name_plural = "trains"
        ordering = ["name"]
