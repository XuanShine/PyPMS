
import os
from datetime import datetime
import pickle

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
def empty_db():

    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Put entries here
    os.rename("certificat", "certificat.save")
    with open("certificat", "wb") as f_out:
        pickle.dump(PRIVATE_KEY_TEST, f_out)

    yield test_db

    os.remove("certificat")
    os.rename("certificat.save", "certificat")

    test_db.drop_tables(MODELS)
    test_db.close()


@pytest.yield_fixture
def empty_db_with_public_key_change():

    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Put entries here
    os.rename("certificat", "certificat.save")
    with open("certificat", "wb") as f_out:
        pickle.dump(PRIVATE_KEY_TEST, f_out)
    
    os.rename('public_key', "public_key.save")
    with open('public_key', 'wb') as f_out:
        f_out.write(PUBLIC_KEY_TEST)

    yield test_db

    os.remove("certificat")
    os.rename("certificat.save", "certificat")
    os.remove('public_key')
    os.rename('public_key.save', "public_key")

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
    def verify(signature, data):
        from Crypto.PublicKey import RSA
        from Crypto.Hash import SHA256
        from Crypto.Signature import PKCS1_PSS

        public_key = RSA.importKey(PUBLIC_KEY_TEST)
        hashage = SHA256.new(data.encode())
        verifier = PKCS1_PSS.new(public_key)
        return verifier.verify(hashage, bytes.fromhex(signature))

    date = datetime.now()
    Paiement.create(
        date=date,
        amount=20,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    assert verify(Paiement.get()._signature, f"{date};20;1")
    Paiement.create(
        date=date,
        amount=30,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay2 = Paiement.get(id=2)
    assert verify(pay2._signature, f"{date};20;1\n{date};30;2")
    pay1 = Paiement.get(id=1)
    assert verify(pay1._signature, f"{date};20;1\n{date};30;2")
    Paiement.create(
        date=date,
        amount=40,
        reservation=Reservation.create(),
        pay_method=PaymentMethod.CB.value,
    )
    pay3 = Paiement.get(id=3)
    pay2 = Paiement.get(id=2)
    assert verify(pay3._signature, f"{date};30;2\n{date};40;3")
    assert verify(pay1._signature, f"{date};20;1\n{date};30;2")
    assert verify(pay2._signature, f"{date};20;1\n{date};30;2\n{date};40;3")


def test_paiement_verify(empty_db):
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    date = datetime.now()
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=40, reservation=Reservation.create())  # 3
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.create(date=date, amount=50, reservation=Reservation.create())  # 4
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.get(id=4).delete_instance()
    assert not all(Paiement.verify(PUBLIC_KEY_TEST))
    for payment in Paiement.select():  # delete all
        payment.delete_instance()

    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 4
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 5
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 6
    assert all(Paiement.verify(PUBLIC_KEY_TEST))
    Paiement.get(id=5).delete_instance()
    assert not all(Paiement.verify(PUBLIC_KEY_TEST))

    for payment in Paiement.select():  # delete all
        payment.delete_instance()

def test_paiement_verify_with_public_key_file(empty_db_with_public_key_change):
    date = datetime.now()
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 1
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 2
    Paiement.create(date=date, amount=20, reservation=Reservation.create())  # 3
    Paiement.create(date=date, amount=30, reservation=Reservation.create())  # 4

    assert all(Paiement.verify())
    Paiement.get(id=1).delete_instance()
    assert not all(Paiement.verify())
