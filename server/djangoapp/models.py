from django.db import models
# from django.utils.timezone import now
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator


class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)

    CAR_TYPES = [
        ("SEDAN", "Sedan"),
        ("SUV", "SUV"),
        ("WAGON", "Wagon"),
        ("COUPE", "Coupe"),
        ("TRUCK", "Truck"),
    ]

    type = models.CharField(max_length=10, choices=CAR_TYPES, default="SUV")
    year = models.IntegerField(
        default=datetime.now().year,
        validators=[MaxValueValidator(datetime.now().year), MinValueValidator(1980)],
    )

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
