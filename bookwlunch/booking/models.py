from django.db import models

class Table(models.Model):
    SHAPE_CHOICES = [
        ('Long', 'Long'),
        ('Round', 'Round')
    ]
    tableID = models.AutoField(primary_key=True)
    seats = models.IntegerField(default=4)
    shape = models.CharField(max_length=10, choices=SHAPE_CHOICES, default='Round')
    is_occupied = models.BooleanField(default=False)
    def __str__(self):
        return f"Table: {self.tableID} - Chairs: {self.seats} - Shape: {self.shape}"
class Customer(models.Model):
    customerID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    phoneNr = models.IntegerField()
    email = models.EmailField()

class Confirmation(models.Model):
    confirmID = models.AutoField(primary_key=True)
    tableID = models.ForeignKey('Table', on_delete=models.CASCADE)
    customerID = models.ForeignKey('Customer', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    booking_date = models.DateField(null=True, blank=True)
    booking_start = models.TimeField(null=True, blank=True)
    booking_end = models.TimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tableID', 'booking_date', 'booking_start', 'booking_end'],
                name='unique_booking'
            )
        ]
