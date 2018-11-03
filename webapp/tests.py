
import os
from datetime import datetime as dt
import datetime
import pickle

from django.utils import timezone

import pytest

# import sys, os
# myPath = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, myPath + '/')

from webapp.models import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


PRIVATE_KEY_TEST = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA6CVto63nraNgMyLL+5YGtPhUibX6NPC4nmPJJlgHhX/Ia68t
ItPP14w0XeMfUgbOLqn5V6+d2U7qVBOG4H2jyKC5FCzOUSVMuCstGvl6x/BW9Mhm
IlmBCpizBSdrEaKjEK2OPnLDz/sLWoaWCDCf6HcvqH5vIcgFDR0fuipUSVwrleSH
XINjtKoLde4gT+YbZlSgr+FR05DYKGgILzsITKzoEsbjsCdBAE0UqQf/VL/4yKWe
0dP2kVmhu2daxNzsZUQeZWEUECo5eNspWrVnu9gHlCP0O5nG1PWCzPPZ5tZmZPc5
7iBVCyfZ5HgpeYgrmKu9gdfC3eOlPh9zXgJJeQIDAQABAoIBAB4t/3rv+NaSDseX
Fn22m1ibkCH3Dngjc1zkDBp4B0JLwnp9Y5jLgJG9IHG0PTYkvFlEr62+nv7JS51y
jG5S5yAGBQmiaZATEU5ADrUbCeNEU4mvI9gDWstN3rgkz76TLi/U4FEuClbXhDpY
lNiruZ43IHL/PONfZYi26JEDP8HpgjQwGhrDIIVEytigerI918D3npRT5e9frxQW
+hvXYtMHHHAtLxLVhdpVWDjvdarK5Gp52gBGW14YEsAvyR9v5DEq9QXqq/891w2x
whZWpyXdwZvm2zutXvEY491GWezPzWD0R9fDAEgzGKwmEL181N4/8To0UKgIN3rS
M/Gu6AECgYEA60yXaHcaA2AZHColy7dHk0eC9nemm3Aq23iThIX3OML02FOtutWN
n3VmLPjnffLNlDs5c2oHhbBz3gRDRHUVitNlzNLGk9d6vaiesl/s/BK/+OkP7lCo
ZD/dyaTj+pCCsnlrCMDx/L4I/ybMDFVhaWhN5u0YUZrBI1hXEO6RPuECgYEA/JHT
TTPbdMAYQ0PADs408mbzVMSIxDtTw9hFi4JHdNgF9ZEjRyQEVk8xWDxGhtf0Vu4b
B0kFD2SFG69fa6sXUTFDVKvaJJSxssDT6G8aOUlG8kEPAFAfdWCyIryMK65+Lvg8
2B22J+O8CKziSrSwqdGDl8dM8AzInyHTepizVZkCgYEAi0IKPg53O9YtJkkfk2DG
oLjrHnmUBlytULUdAYrT1Sk1Ba8InBH1vpEZxrYNM7J2zyr6Bn+TMiFLgfOd6C8v
b7lLf5yjYC5ge00Hl2REeq+SJHuzLQVZk/NkjQnkz4+leoF3wneHAGFsK65Hh2kk
vOC5clmSUgG4GvYWmXPITKECgYEAoOP0CrYCEnlb+11pNwU8zT2vvEwGI5r3XUaj
5p7zDgeepDP0mRjkemawNFkRREzFJatAJH/rbUbHVD9/NYMjs2ECVymyKKNgH1Ke
qu47ckqvmxq+h6CCqa8TSvV5BUp+r0UK3VDv/LEh0xTuglBgSY1hmoonBLPgCR7v
LKWhd+ECgYAkCBadx+PeZ2KHi+Hq9w4vtiJc1MNUBieyXwWqYvXmOK6C7nX7Pykl
VP/eYkCeY6akd7xhA8hWoBZFqcoq6+27MqZzPPnZLejW3XosvF7Qki1nOAWu/ztt
LUQFDEEcURztY6/IMP/tDNc301Mca4GBCJGI2gfLxrqL8OD/3Bed+Q==
-----END RSA PRIVATE KEY-----"""
PUBLIC_KEY_TEST = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6CVto63nraNgMyLL+5YG
tPhUibX6NPC4nmPJJlgHhX/Ia68tItPP14w0XeMfUgbOLqn5V6+d2U7qVBOG4H2j
yKC5FCzOUSVMuCstGvl6x/BW9MhmIlmBCpizBSdrEaKjEK2OPnLDz/sLWoaWCDCf
6HcvqH5vIcgFDR0fuipUSVwrleSHXINjtKoLde4gT+YbZlSgr+FR05DYKGgILzsI
TKzoEsbjsCdBAE0UqQf/VL/4yKWe0dP2kVmhu2daxNzsZUQeZWEUECo5eNspWrVn
u9gHlCP0O5nG1PWCzPPZ5tZmZPc57iBVCyfZ5HgpeYgrmKu9gdfC3eOlPh9zXgJJ
eQIDAQAB\n-----END PUBLIC KEY-----"""


@pytest.yield_fixture
@pytest.mark.django_db
def db_guest():
    # Put entries here
    guests = ["paul", "jean", "dominique", "joseph", "antoine", "philippe", "jacques"]
    guests = [Guest(name=name) for name in guests]
    for guest in guests:
        guest.save()

    yield guests


@pytest.yield_fixture
def empty_db_with_public_key_change():
    # Put entries here
    os.rename(BASE_DIR + "/certificat", BASE_DIR + "/certificat.save")
    with open(BASE_DIR + "/certificat", "wb") as f_out:
        pickle.dump(PRIVATE_KEY_TEST, f_out)
    
    os.rename(BASE_DIR + '/public_key', BASE_DIR + "/public_key.save")
    with open(BASE_DIR + '/public_key', 'wb') as f_out:
        f_out.write(PUBLIC_KEY_TEST)

    yield None

    os.remove(BASE_DIR + "/certificat")
    os.rename(BASE_DIR + "/certificat.save", BASE_DIR + "/certificat")
    os.remove(BASE_DIR + '/public_key')
    os.rename(BASE_DIR + '/public_key.save', BASE_DIR + "/public_key")


@pytest.mark.django_db
def test_society():
    Society.objects.create(name="")
    assert len(Society.objects.all()) == 1

    Society.objects.create(name="SAS JPD Hotel", address="06130 Grasse")
    assert len(Society.objects.all()) == 2
    assert Society.objects.get(id=2).name == "SAS JPD Hotel"

@pytest.mark.django_db
def test_guest():
    jean = Guest(name="jean")
    jean.save()
    antoine = Guest(name="antoine")
    antoine.save()
    assert Guest.objects.get(name="jean").name == "jean"
    assert Guest.objects.get(name= "antoine").name == "antoine"

    jpd = Society(name="SAS JPD Hotel", address="06130 Grasse")
    nguyen_invest = Society(name="Nguyen Invest", address="06130 Grasse")
    jpd.save()
    nguyen_invest.save()
    jean.society = jpd
    antoine.society = jpd
    jean.save()
    antoine.save()
    assert Society.objects.get(name="SAS JPD Hotel").employees.count() == 2
    assert not Society.objects.get(name= "Nguyen Invest").employees.count()


@pytest.mark.django_db
def test_reservation(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()
    res_02_01_2018 = Reservation()
    res_02_01_2018.save()

    res_01_01_2018.guests.add(db_guest[0])  # paul
    assert res_01_01_2018 in db_guest[0].reservations.all()

    db_guest[1].reservations.add(res_02_01_2018)
    db_guest[1].reservations.add(res_01_01_2018)
    assert db_guest[1] in res_02_01_2018.guests.all()
    assert db_guest[1] in res_01_01_2018.guests.all()
    assert res_01_01_2018.guests.count() == 2
    assert db_guest[1].reservations.count() == 2

    # TODO: à tester reservation.total_price()

@pytest.mark.django_db
def test_stay(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    stay1 = Stay(
        prices="50 50",
        check_in=dt(2018, 1, 1),
        check_out=dt(2018, 1, 3),
        reservation=res_01_01_2018,
        room=101,
    )
    stay1.save()

    res_01_01_2018.guests.add(db_guest[0])  # paul

    assert stay1.price() == 100
    assert res_01_01_2018.total_price() == 100

    stay2 = Stay(
        prices="60 50",
        check_in=dt(2018, 1, 1),
        check_out=dt(2018, 1, 3),
        reservation=res_01_01_2018,
        room=102,
    )
    stay2.save()

    assert stay2.price() == 110
    assert res_01_01_2018.total_price() == 210

@pytest.mark.django_db
def test_stay_title(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    stay1 = Stay(
        prices="50 50",
        check_in=dt(2018, 1, 1),
        check_out=dt(2018, 1, 3),
        reservation=res_01_01_2018,
        room=101,
        name="jean",
    )
    stay1.save()

    assert stay1.title() == "jean"

    stay2 = Stay(
        prices="60 50",
        check_in=dt(2018, 1, 1),
        check_out=dt(2018, 1, 3),
        reservation=res_01_01_2018,
        room=102,
    )
    stay2.save()
    assert stay2.title() == "No Name"

    res_01_01_2018.guests.add(db_guest[0])  # paul

    assert stay2.title() == "paul"

    res_01_01_2018.guests.add(db_guest[1])  # jean

    assert stay2.title() == "paul - jean"

@pytest.mark.django_db
def test_paiement(db_guest):
    res_01_01_2018 = Reservation()
    res_01_01_2018.save()

    paiement1 = Paiement(amount=30, reservation=res_01_01_2018)
    paiement1.set_pay_method(PaymentMethod.CB)
    paiement1.save()

    assert res_01_01_2018.paiements.all()[0].amount == 30

    paiement2 = Paiement.objects.create(amount=20, reservation=res_01_01_2018)
    assert res_01_01_2018.paiements.all()[1].amount == 20
    assert res_01_01_2018.paiements.all()[1].get_pay_method() == PaymentMethod.AUTRE
    paiement2.set_pay_method(PaymentMethod.CB)
    paiement2.save()
    assert res_01_01_2018.paiements.all()[1].get_pay_method() == PaymentMethod.CB

@pytest.mark.django_db
def test_product():
    Product.objects.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    assert Product.objects.all()[0].name == "Soda (33cl)"

    boisson = CategoryProduct.objects.create(name="boisson")
    soda = Product.objects.get(name="Soda (33cl)")
    soda.category = boisson
    soda.save()

    assert soda in boisson.products.all()

@pytest.mark.django_db
def test_sale():
    res = Reservation.objects.create()
    p1 = Product.objects.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    p2 = Product.objects.create(name="Breakfast", initial_price=8, tax=0.1)
    s1 = Sale.objects.create(
        date=dt(2018, 1, 1), reservation=res, product=p1, price=1, quantity=3
    )
    s2 = Sale.objects.create(date=dt(2018, 1, 2), reservation=res, product=p2, quantity=2)
    assert s1.total_price() == 3
    assert s2.total_price() == 16
    assert res.total_price() == 19

@pytest.mark.django_db
def test_reservation_total_price():
    res = Reservation.objects.create()
    p1 = Product.objects.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    p2 = Product.objects.create(name="Breakfast", initial_price=8, tax=0.1)
    s1 = Sale.objects.create(
        date=dt(2018, 1, 1), reservation=res, product=p1, price=1, quantity=3
    )
    s2 = Sale.objects.create(date=dt(2018, 1, 2), reservation=res, product=p2, quantity=2)
    stay1 = Stay.objects.create(
        prices="50 50",
        check_in=dt(2018, 1, 1),
        check_out=dt(2018, 1, 3),
        reservation=res,
        room=101,
        name="jean",
    )

    assert res.total_price() == 119


@pytest.mark.django_db
def test_paiement_signature(empty_db_with_public_key_change):
    def verify(signature, data):
        import os
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.exceptions import InvalidSignature
        public_key = serialization.load_pem_public_key(PUBLIC_KEY_TEST,
                                                    backend=default_backend())
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


    date = timezone.now()
    Paiement.create(
        date=date,
        amount=20,
        reservation=Reservation.objects.create(),
        pay_method=PaymentMethod.CB.value,
    )
    assert Paiement.objects.count() == 1
    assert verify(Paiement.objects.get()._signature, f"{date};20.00;1")
    Paiement.create(
        date=date,
        amount=30,
        reservation=Reservation.objects.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay2 = Paiement.objects.get(id=2)
    assert Paiement.objects.get(id=1)._signature == Paiement.objects.get(id=2)._signature
    assert verify(pay2._signature, f"{date};20.00;1\n{date};30.00;2")
    pay1 = Paiement.objects.get(id=1)
    assert verify(pay1._signature, f"{date};20.00;1\n{date};30.00;2")
    Paiement.create(
        date=date,
        amount=40,
        reservation=Reservation.objects.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay3 = Paiement.objects.get(id=3)
    pay2 = Paiement.objects.get(id=2)
    assert verify(pay3._signature, f"{date};30.00;2\n{date};40.00;3")
    assert verify(pay1._signature, f"{date};20.00;1\n{date};30.00;2")
    assert verify(pay2._signature, f"{date};20.00;1\n{date};30.00;2\n{date};40.00;3")

@pytest.mark.django_db
def test_paiement_verify(empty_db_with_public_key_change):
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    date = dt.now()
    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 1
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 2
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=40, reservation=Reservation.objects.create())  # 3
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=50, reservation=Reservation.objects.create())  # 4
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.objects.get(id=4).delete()
    assert not all(Paiement.verify(PUBLIC_KEY_TEST))
    for payment in Paiement.objects.all():  # delete all
        payment.delete()

    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 4
    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 5
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 6
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.objects.get(id=5).delete()
    assert not all(Paiement.verify(PUBLIC_KEY_TEST))

    for payment in Paiement.objects.all():  # delete all
        payment.delete()

@pytest.mark.django_db
def test_paiement_verify_with_public_key_file(empty_db_with_public_key_change):
    date = dt.now()
    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.objects.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.objects.create())  # 4

    assert all(Paiement.verify())
    Paiement.objects.get(id=1).delete()
    assert not all(Paiement.verify())

@pytest.mark.django_db
def test_insert_new():
    assert not Guest.objects.all()
    assert not Stay.objects.all()
    assert not Reservation.objects.all()
    Stay.insert_new("Paul", dt(2018, 1, 1).date(), dt(2018, 1, 2).date(), 101, "50", "")
    assert Guest.objects.count() == 1
    assert Stay.objects.count() == 1
    assert Reservation.objects.count() == 1
    assert Reservation.objects.all()[0] in Guest.objects.get(name="Paul").reservations.all()
    res = Reservation()
    res.save()
    Stay.insert_new("Jean", dt(2018, 1, 1).date(), dt(2018, 1, 2).date(), 101, "50", "", in_res=res)
    Stay.insert_new("Dom", dt(2018, 1, 1).date(), dt(2018, 1, 2).date(), 102, "50", "", in_res=res)
    assert Guest.objects.count() == 3
    assert Stay.objects.count() == 3
    assert Reservation.objects.count() == 2
    assert res in Guest.objects.get(name="Jean").reservations.all()
    assert res in Guest.objects.get(name="Dom").reservations.all()


@pytest.mark.django_db
def test_get_stays_between():
    res = Reservation()
    res.save()
    stay1 = Stay(
        check_in=dt(2018, 1, 10), check_out=dt(2018, 1, 20), reservation=res, room=101
    )  # yes
    stay2 = Stay(
        check_in=dt(2018, 1, 15), check_out=dt(2018, 1, 20), reservation=res, room=101
    )  # no
    stay3 = Stay(
        check_in=dt(2018, 1, 14), check_out=dt(2018, 1, 15), reservation=res, room=101
    )  # yes
    stay4 = Stay(
        check_in=dt(2018, 1, 15), check_out=dt(2018, 1, 16), reservation=res, room=101
    )  # no
    stay5 = Stay(
        check_in=dt(2018, 1, 9), check_out=dt(2018, 1, 10), reservation=res, room=101
    )  # no
    stay6 = Stay(
        check_in=dt(2018, 1, 8), check_out=dt(2018, 1, 9), reservation=res, room=101
    )  # no
    stay1.save()
    stay2.save()
    stay3.save()
    stay4.save()
    stay5.save()
    stay6.save()
    expected = list(Stay.get_stays_between(dt(2018, 1, 10), dt(2018, 1, 15)))
    assert stay1 in expected
    assert stay2 not in expected
    assert stay3 in expected
    assert stay4 not in expected
    assert stay5 not in expected
    assert stay6 not in expected

@pytest.mark.django_db
def test_stay_with_datetime_as_input():
    res = Reservation()
    res.save()
    stay1 = Stay(
        check_in=dt(2018, 1, 10), check_out=dt(2018, 1, 20), reservation=res, room=101
    )
    stay1.save()
    assert type(Stay.objects.get(id=stay1.id).check_in) == datetime.date
    assert not type(Stay.objects.get(id=stay1.id).check_in) == datetime.datetime


@pytest.mark.skip(reason="TODO")
@pytest.mark.django_db
def test_stay_with_timezone_as_input():
    pass