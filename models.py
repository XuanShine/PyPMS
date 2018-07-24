
from datetime import datetime
from enum import Enum

from peewee import *


database = SqliteDatabase("reservation.db")


PaymentMethod = Enum(
    "PaymentMethod", "CB ESPECE CHEQUE CHEQUE_VACANCE VAD VIREMENT AUTRE"
)


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
            stays_price = sum(stay.price() for stay in self.stays) or 0
            products_price = sum(product.total_price() for product in self.sales) or 0
            return float(stays_price) + float(products_price)
        except AttributeError as e_info:
            raise AttributeError(e_info)


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
            return "No Name"
        return self.name


class Paiement(BaseModel):
    date = DateTimeField(default=datetime.now())
    amount = DecimalField(default=0)
    reservation = ForeignKeyField(Reservation, backref="paiements")
    pay_method = IntegerField(default=None, null=True)
    notes = CharField(default="")
    _signature = CharField(default="", null=True)

    def set_pay_method(self, method: PaymentMethod):
        self.pay_method = method.value

    def get_pay_method(self) -> PaymentMethod:
        if not self.pay_method:
            return PaymentMethod.AUTRE
        return PaymentMethod(self.pay_method)

    @classmethod
    def create(cls, *args, **kwargs):
        def sign(data):
            # TODO: to complete
            return data

        pay = super().create(*args, **kwargs)
        payments = list(cls.select())
        sign_tmp = sign(f"{pay.date};{pay.amount};{pay.reservation.id}")
        if len(payments) == 1:
            pay._signature = sign_tmp
            pay.save()
        else:
            prev = payments[-2]
            pay._signature = sign(
                f"{prev.date};{prev.amount};{prev.reservation.id}\n{sign_tmp}"
            )
            pay.save()
            if len(payments) == 2:
                prev._signature = pay._signature
                prev.save()
            else:
                prev._signature = sign(prev._signature + "\n" + sign_tmp)
                prev.save()
        return pay

    @classmethod
    def verify(cls):
        def verify_sign(data, hash):
            # TODO: to complete
            return (
                "\n".join(
                    [f"{d.date};{d.amount};{d.reservation.id}" for d in data if d]
                )
                == hash
            )

        def tmp_verify(x, y, z, tail):
            if not tail:
                return [verify_sign((y, z), z._signature)]
            return [verify_sign((x, y, z), y._signature)] + tmp_verify(
                y, z, tail[0], tail[1:]
            )

        payments = list(cls.select())
        if not payments:
            return [True]
        elif len(payments) == 1:
            return [verify_sign(("", payments[0]), payments[0]._signature)]
        return tmp_verify("", payments[0], payments[1], payments[2:])


class CategoryProduct(BaseModel):
    name = CharField()


class Product(BaseModel):
    name = CharField()
    initial_price = FloatField()
    category = ForeignKeyField(
        CategoryProduct, backref="products", null=True, default=None
    )
    tax = FloatField(default=0.2)
    stock = IntegerField(default=-1)


class Sale(BaseModel):
    date = DateTimeField(default=datetime.now())
    product = ForeignKeyField(Product, backref="sales")
    reservation = ForeignKeyField(Reservation, backref="sales")
    price = FloatField(default=None, null=True)
    quantity = IntegerField(default=1)

    def total_price(self):
        if not self.price:
            self.price = self.product.initial_price
        return float(self.quantity * self.price)


def create_tables():
    with database:
        database.create_tables(
            [
                Society,
                Guest,
                Reservation,
                Stay,
                Paiement,
                GuestReservation,
                CategoryProduct,
                Product,
                Sale,
            ]
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
    GuestReservation, CategoryProduct, Product, Sale])
"""
