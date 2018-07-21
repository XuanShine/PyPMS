
from datetime import datetime
from peewee import *
from enum import Enum

database = SqliteDatabase("reservation.db")


Payment_Method = Enum('Payment_Method', 'CB ESPECE CHEQUE CHEQUE_VACANCE VAD VIREMENT AUTRE')

class BaseModel(Model):
    class Meta:
        database = database


class Society(BaseModel):
    name = CharField(default="")
    address = CharField(default="")
    notes = TextField(default="")

    def __repr__(self):
        return self.name


class Guest(BaseModel):
    name = CharField(default="")
    birthday = DateField(default="")
    address = CharField(default="")
    society = ForeignKeyField(Society, backref="employees", default=None, null=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    guests = ManyToManyField(Guest, backref="reservations")
    notes = TextField(default="")

    def total_price(self):
        try:
            stays = self.stays
        except AttributeError:
            raise Exception("La réservation n'est lié à aucun séjour")
        return sum(stay.price() for stay in stays)


GuestReservation = Reservation.guests.get_through_model()


class Stay(BaseModel):
    prices = CharField(default="")
    check_in = DateTimeField(default="")
    check_out = DateTimeField(default="")
    notes = TextField(default="")
    reservation = ForeignKeyField(Reservation, backref="stays")
    room = IntegerField()
    name = CharField(default="")

    def price(self):
        return sum(map(float, self.prices.strip().split()))

    def title(self):
        if not self.name:
            if self.reservation and self.reservation.guests:
                return " - ".join(map(str, list(self.reservation.guests)))
            else:
                return "No Name"
        return self.name


class Paiement(BaseModel):
    date = DateTimeField(default=datetime.now())
    amount = DecimalField(default=0)
    reservation = ForeignKeyField(Reservation, backref="paiements")
    pay_method = IntegerField(default=None, null=True)
    notes = CharField(default='')

    def set_pay_method(self, method: Payment_Method):
        self.pay_method = method.value

    def get_pay_method(self) -> Payment_Method:
        if not self.pay_method:
            return Payment_Method.AUTRE
        return Payment_Method(self.pay_method)

def create_tables():
    with database:
        database.create_tables(
            [Society, Guest, Reservation, Stay, Paiement, GuestReservation]
        )


"""
database.drop_tables([
    Guest,
    Society,
    Stay,
    Paiement,
    Reservation,
    GuestReservation])
database.create_tables([
    Guest,
    Society,
    Stay,
    Paiement,
    Reservation,
    GuestReservation])
"""
