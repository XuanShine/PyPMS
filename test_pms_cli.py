

import pytest
from datetime import datetime as dt

from models import *
from pms_cli import *

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
def pms_empty_db():
    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    yield PMS_CLI()

    test_db.drop_tables(MODELS)
    test_db.close()


@pytest.yield_fixture
def pms():
    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    # Put entries here
    #    | 5| 6| 7| 8| 9|10|11|12|13|14|15|16|17|18|19|20
    # 101| a| a| b| b| b| c|  | d| d| e| b| b|  | b|  |
    # 102|  |  |  | e| e| f| d| d|  |  |  |  |  |  |  |
    # 103|  |  |  | e| e| g|  | h| h| h| h| h| h|  |  |
    # 104|  |  |  |  |  | d| d| d|  |  |  |  |  |  |  |

    yield PMS_CLI()

    test_db.drop_tables(MODELS)
    test_db.close()


def test_quit(pms_empty_db):
    with pytest.raises(SystemExit) as e_info:
        pms_empty_db.quit()


def test_get_stays_between(pms_empty_db):
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
    expected = list(get_stays_between(dt(2018, 1, 10), dt(2018, 1, 15)))
    assert stay1 in expected
    assert stay2 not in expected
    assert stay3 in expected
    assert stay4 not in expected
    assert stay5 not in expected
    assert stay6 not in expected


def test_insert_new(pms_empty_db):
    assert not list(Guest.select())
    assert not list(Stay.select())
    assert not list(Reservation.select())
    insert_new("Paul", dt(2018, 1, 1), dt(2018, 1, 2), 101, "50", "")
    assert len(list(Guest.select())) == 1
    assert len(list(Stay.select())) == 1
    assert len(list(Reservation.select())) == 1
    assert Reservation.select()[0] in Guest.get(Guest.name == "Paul").reservations
    res = Reservation()
    res.save()
    insert_new("Jean", dt(2018, 1, 1), dt(2018, 1, 2), 101, "50", "", in_res=res)
    insert_new("Dom", dt(2018, 1, 1), dt(2018, 1, 2), 102, "50", "", in_res=res)
    assert len(list(Guest.select())) == 3
    assert len(list(Stay.select())) == 3
    assert len(list(Reservation.select())) == 2
    assert res in Guest.get(Guest.name == "Jean").reservations
    assert res in Guest.get(Guest.name == "Dom").reservations


def test_payment(pms_empty_db):
    res = Reservation.create()
    payment(res, dt.today(), 23, PaymentMethod.CB, "Test notes")
    assert Paiement.select()[0].amount == 23
    assert Paiement.select()[0].get_pay_method() == PaymentMethod.CB
    assert Paiement.select()[0].date.strftime("%d%m%Y") == dt.today().strftime("%d%m%Y")
    assert Paiement.select()[0].reservation == res
    assert Paiement.select()[0].notes == "Test notes"


def test_sell_product(pms_empty_db):
    prod = Product.create(name="Soda (33cl)", initial_price=1.2, tax=0.2)
    sell_product(prod)
    assert Reservation.select()
    assert Reservation.get(id=1).sales.get().product == prod
