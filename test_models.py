
from datetime import datetime

import pytest

from models import *

MODELS = [
    Society,
    Guest,
    Stay,
    Paiement,
    Reservation,
    GuestReservation,
    CategoryProduct,
    Product,
    Sale,
]


@pytest.yield_fixture
def empty_db():

    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Put entries here

    yield test_db

    test_db.drop_tables(MODELS)
    test_db.close()


@pytest.yield_fixture
def db_guest():
    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Put entries here
    guests = ["paul", "jean", "dominique", "joseph", "antoine", "philippe", "jacques"]
    guests = [Guest(name=name) for name in guests]
    for guest in guests:
        guest.save()

    yield guests

    test_db.drop_tables(MODELS)
    test_db.close()


def test_society(empty_db):
    empty_society = Society(name="")
    empty_society.save()

    jpd = Society(name="SAS JPD Hotel", address="06130 Grasse")
    assert len(list(Society.select())) == 1
    assert jpd.name == "SAS JPD Hotel"


def test_guest(empty_db):
    jean = Guest(name="jean")
    jean.save()
    antoine = Guest(name="antoine")
    antoine.save()
    assert Guest.get(Guest.name == "jean").name == "jean"
    assert Guest.get(Guest.name == "antoine").name == "antoine"

    jpd = Society(name="SAS JPD Hotel", address="06130 Grasse")
    nguyen_invest = Society(name="Nguyen Invest", address="06130 Grasse")
    jpd.save()
    nguyen_invest.save()
    jean.society = jpd
    antoine.society = jpd
    jean.save()
    antoine.save()
    assert len(list(Society.get(Society.name == "SAS JPD Hotel").employees)) == 2
    assert not list(Society.get(Society.name == "Nguyen Invest").employees)


def test_reservation(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()
    res_02_01_2018 = Reservation()
    res_02_01_2018.save()

    res_01_01_2018.guests.add(db_guest[0])  # paul
    assert res_01_01_2018 in list(db_guest[0].reservations)

    db_guest[1].reservations.add(res_02_01_2018)
    db_guest[1].reservations.add(res_01_01_2018)
    assert db_guest[1] in res_02_01_2018.guests
    assert db_guest[1] in res_01_01_2018.guests
    assert len(list(res_01_01_2018.guests)) == 2
    assert len(list(db_guest[1].reservations)) == 2

    # à tester reservation.total_price()


def test_stay(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    stay1 = Stay(
        prices="50 50",
        check_in=datetime(2018, 1, 1),
        check_out=datetime(2018, 1, 3),
        reservation=res_01_01_2018,
        room=101,
    )
    stay1.save()

    res_01_01_2018.guests.add(db_guest[0])  # paul

    assert stay1.price() == 100
    assert res_01_01_2018.total_price() == 100

    stay2 = Stay(
        prices="60 50",
        check_in=datetime(2018, 1, 1),
        check_out=datetime(2018, 1, 3),
        reservation=res_01_01_2018,
        room=102,
    )
    stay2.save()

    assert stay2.price() == 110
    assert res_01_01_2018.total_price() == 210


def test_stay_title(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    stay1 = Stay(
        prices="50 50",
        check_in=datetime(2018, 1, 1),
        check_out=datetime(2018, 1, 3),
        reservation=res_01_01_2018,
        room=101,
        name="jean",
    )
    stay1.save()

    assert stay1.title() == "jean"

    stay2 = Stay(
        prices="60 50",
        check_in=datetime(2018, 1, 1),
        check_out=datetime(2018, 1, 3),
        reservation=res_01_01_2018,
        room=102,
    )
    stay2.save()
    assert stay2.title() == "No Name"

    res_01_01_2018.guests.add(db_guest[0])  # paul

    assert stay2.title() == "paul"

    res_01_01_2018.guests.add(db_guest[1])  # jean

    assert stay2.title() == "paul - jean"


def test_paiement(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    paiement1 = Paiement(amount=30, reservation=res_01_01_2018)
    paiement1.set_pay_method(PaymentMethod.CB)
    paiement1.save()

    assert res_01_01_2018.paiements[0].amount == 30

    paiement2 = Paiement.create(amount=20, reservation=res_01_01_2018)
    assert res_01_01_2018.paiements[1].amount == 20
    assert res_01_01_2018.paiements[1].get_pay_method() == PaymentMethod.AUTRE
    paiement2.set_pay_method(PaymentMethod.CB)
    paiement2.save()
    assert res_01_01_2018.paiements[1].get_pay_method() == PaymentMethod.CB


def test_product(empty_db):
    Product.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    assert Product.select()[0].name == "Soda (33cl)"

    boisson = CategoryProduct.create(name="boisson")
    soda = Product.get(Product.name == "Soda (33cl)")
    soda.category = boisson
    soda.save()

    assert soda in boisson.products


def test_sale(empty_db):
    res = Reservation.create()
    p1 = Product.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    p2 = Product.create(name="Breakfast", initial_price=8, tax=0.1)
    s1 = Sale.create(
        date=datetime(2018, 1, 1), reservation=res, product=p1, price=1, quantity=3
    )
    s2 = Sale.create(date=datetime(2018, 1, 2), reservation=res, product=p2, quantity=2)
    assert s1.total_price() == 3
    assert s2.total_price() == 16
    assert res.total_price() == 19


def test_reservation_total_price(empty_db):
    res = Reservation.create()
    p1 = Product.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    p2 = Product.create(name="Breakfast", initial_price=8, tax=0.1)
    s1 = Sale.create(
        date=datetime(2018, 1, 1), reservation=res, product=p1, price=1, quantity=3
    )
    s2 = Sale.create(date=datetime(2018, 1, 2), reservation=res, product=p2, quantity=2)
    stay1 = Stay.create(
        prices="50 50",
        check_in=datetime(2018, 1, 1),
        check_out=datetime(2018, 1, 3),
        reservation=res,
        room=101,
        name="jean",
    )

    assert res.total_price() == 119


def test_paiement_signature(empty_db):
    date = datetime.now()
    Paiement.create(
        date=date,
        amount=20,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    assert Paiement.get()._signature == f"{date};20;1"
    Paiement.create(
        date=date,
        amount=30,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay2 = Paiement.get(id=2)
    assert pay2._signature == f"{date};20;1\n{date};30;2"
    pay1 = Paiement.get(id=1)
    assert pay1._signature == f"{date};20;1\n{date};30;2"
    Paiement.create(
        date=date,
        amount=40,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay3 = Paiement.get(id=3)
    pay2 = Paiement.get(id=2)
    assert pay3._signature == f"{date};30;2\n{date};40;3"
    assert pay1._signature == f"{date};20;1\n{date};30;2"
    assert pay2._signature == f"{date};20;1\n{date};30;2\n{date};40;3"


def test_paiement_verify(empty_db):
    assert all(Paiement.verify())
    date = datetime.now()
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    assert all(Paiement.verify())
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    assert all(Paiement.verify())
    Paiement.create(date=date, amount=40, reservation=Reservation.create())  # 3
    assert all(Paiement.verify())
    Paiement.create(date=date, amount=50, reservation=Reservation.create())  # 4
    assert all(Paiement.verify())
    Paiement.get(id=4).delete_instance()
    assert not all(Paiement.verify())
    for payment in Paiement.select():  # delete all
        payment.delete_instance()

    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 4
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 5
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 6
    assert all(Paiement.verify())
    Paiement.get(id=5).delete_instance()
    assert not all(Paiement.verify())

    for payment in Paiement.select():  # delete all
        payment.delete_instance()

    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 4
    assert all(Paiement.verify())
    Paiement.get(id=1).delete_instance()
    assert not all(Paiement.verify())
