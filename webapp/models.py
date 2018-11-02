#!/usr/bin/env python3
from enum import Enum

from django.db import models
from django.db.models import (CharField, TextField, DateField, DateTimeField,
    ForeignKey, ManyToManyField, IntegerField, FloatField, DecimalField)
from django.utils import timezone

# Create your models here.

PaymentMethod = Enum(
    "PaymentMethod", "CB ESPECE CHEQUE CHEQUE_VACANCE VAD VIREMENT AUTRE"
)

StayStatus = Enum(
    "StayStatus", "DRAFT CONFIRMED CHECKED-IN CHECKED-OUT CLOSE"
)

class Society(models.Model):
    name = CharField(max_length=50, default="")
    address = CharField(max_length=100, default="")
    notes = TextField(default="")

    def __repr__(self):
        return self.name


class Guest(models.Model):
    name = CharField(max_length=50, default="")
    birthday = DateField(blank=True, null=True)
    address = CharField(max_length=100, default="")
    society = ForeignKey(
        "Society",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
    )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class Reservation(models.Model):
    guests = ManyToManyField(
        Guest,
        related_name="reservations",
        blank=True)
    notes = TextField(default="")

    def total_price(self):
        try:
            stays_price = sum(stay.price() for stay in self.stays.all()) or 0
            products_price = sum(product.total_price() for product in self.sales.all()) or 0
            return float(stays_price) + float(products_price)
        except AttributeError as e_info:
            raise AttributeError(e_info)

class Stay(models.Model):
    prices = TextField(default="")
    check_in = DateTimeField(blank=True, null=True)
    check_out = DateTimeField(blank=True, null=True)
    notes = TextField(default="")
    reservation = ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stays")
    room = IntegerField()
    name = CharField(max_length=50, default="")
    status = IntegerField(default=StayStatus.DRAFT.value)

    def price(self):
        return sum(map(float, self.prices.strip().split()))

    def title(self):
        if not self.name:
            if self.reservation and self.reservation.guests.all():
                return " - ".join(map(str, list(self.reservation.guests.all())))
            return "No Name"
        return self.name


class Paiement(models.Model):
    date = DateTimeField(default=timezone.now)
    amount = DecimalField(max_digits=10, decimal_places=2, default=0)
    reservation = ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="paiements")
    pay_method = IntegerField(blank=True, null=True)
    notes = TextField(default="")
    _signature = CharField(max_length=500, default="", null=True)

    def set_pay_method(self, method: PaymentMethod):
        self.pay_method = method.value

    def get_pay_method(self) -> PaymentMethod:
        if not self.pay_method:
            return PaymentMethod.AUTRE
        return PaymentMethod(self.pay_method)

    @classmethod
    def create(cls, **kwargs) -> bytes:
        def sign(data: str) -> str(hex):
            import os
            import pickle
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))

            with open(os.path.join(BASE_DIR, "certificat"), "rb") as f_in:
                key = pickle.load(f_in)
                key = serialization.load_pem_private_key(key, password=None,
                                                            backend=default_backend())

            signature = key.sign(
                data.encode(),
                padding.PSS(
                    mgf = padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()

        pay = cls.objects.create(**kwargs)
        pay_db = cls.objects.get(id=pay.id)

        payments = list(cls.objects.all())
        data = f"{pay_db.date};{pay_db.amount};{pay_db.reservation.id}"
        if len(payments) == 1:
            pay_db._signature = sign(data)
            pay_db.save()
        else:
            prev = payments[-2]
            pay_db._signature = sign(
                f"{prev.date};{prev.amount};{prev.reservation.id}\n{data}"
            )
            pay_db.save()
            if len(payments) == 2:
                prev._signature = pay_db._signature
                prev.save()
            else:
                prev2 = payments[-3]
                prev._signature = sign(
                    "\n".join(
                        [
                            f"{d.date};{d.amount};{d.reservation.id}"
                            for d in (prev2, prev, pay_db)
                            if d
                        ]
                    )
                )
                prev.save()

        return pay_db

    @classmethod
    def verify(cls, public_key:bytes=None):
        import os
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.exceptions import InvalidSignature

        BASE_DIR = os.path.abspath(os.path.dirname(__file__))

        if not public_key:
            with open(os.path.join(BASE_DIR, 'public_key'), 'r') as f_in:
                public_key = f_in.read().encode()

        public_key = serialization.load_pem_public_key(public_key,
                                                        backend=default_backend())

        def verify_sign(data, signature):
            data = "\n".join(
                [f"{d.date};{d.amount};{d.reservation.id}" for d in data if d]
            )

            try:
                public_key.verify(
                    bytes.fromhex(signature),
                    data.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                return False

        def tmp_verify(x, y, z, tail):
            if not tail:
                return [verify_sign((y, z), z._signature)]
            return [verify_sign((x, y, z), y._signature)] + tmp_verify(
                y, z, tail[0], tail[1:]
            )

        payments = list(cls.objects.all())
        if not payments:
            return [True]
        elif len(payments) == 1:
            return [verify_sign(("", payments[0]), payments[0]._signature)]
        return tmp_verify("", payments[0], payments[1], payments[2:])


class CategoryProduct(models.Model):
    name = CharField(max_length=50)

class Product(models.Model):
    name = CharField(max_length=50)
    initial_price = FloatField()
    category = ForeignKey(
        CategoryProduct,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True
    )
    tax = FloatField(default=0.2)
    stock = IntegerField(default=-1)


class Sale(models.Model):
    date = DateTimeField(default=timezone.now)
    product = ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales")
    reservation = ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales")
    price = FloatField(default=None, null=True)
    quantity = IntegerField(default=1)

    def total_price(self):
        if not self.price:
            self.price = self.product.initial_price
        return float(self.quantity * self.price)
