
import sys
from datetime import datetime as dt
from datetime import timedelta

from texttable import Texttable

from models import *

main_menu = """\
cal - Voir calendrier - ex: "cal:22/3/2018" ou "cal-6" ou "cal+10" ou "cal" (aujourd'hui)
new - Nouvelle réservation
s{chambre}-{date} - selectionne la réservation - ex: s102-18/07 ou s103-14/08/2017
v - Verifier l'intégrité des transactions
q - Quit
"""

MESSAGE_IN_STAY_SELECTION = """\
r - Voir la réservation
m - Modifier
c - Cancel
p - payer
XXX - Changer numéro de chambre ex: 402
"""

MESSAGE_IN_PAYMENT = """\
 1: CB, 2: ESPECE, 3: CHEQUE, 4: CHEQUE_VACANCE, 5: VAD, 6: VIREMENT, 7: AUTRE
"""

# ROOMS = [301, 302, 303, 304, 305, 306, 307, 308,
#         401, 402, 403, 404, 405, 406, 407, 408,
#         501, 502, 503, 504, 505, 506, 507, 508]
ROOMS = [101, 102, 103, 104]


def get_stays_between(start, end):
    query = Stay.select().where((Stay.check_out > start) & (Stay.check_in < end))
    return query


def insert_new(
    name,
    check_in: dt,
    check_out: dt,
    room: int,
    prices: str,
    notes,
    in_res: Reservation = None,
):
    res = in_res or Reservation(notes=notes)
    res.save()
    stay = Stay(
        reservation=res,
        check_in=check_in,
        check_out=check_out,
        room=room,
        prices=prices,
    )
    stay.save()
    guest = Guest(name=name)
    guest.save()
    guest.reservations.add(res)


def sell_product(
    product: Product, date=dt.now(), price=None, quantity=1, in_res: Reservation = None
):
    if not in_res:
        in_res = Reservation.create()
    if not price:
        price = product.initial_price
    Sale.create(
        date=date, price=price, product=product, reservation=in_res, quantity=quantity
    )


def payment(
    reservation: Reservation, date, amount: float, method: PaymentMethod, notes: str
):
    pay = Paiement.create(
        reservation=reservation,
        date=date,
        amount=amount,
        notes=notes,
        pay_method=method.value,
    )


class PMS_CLI:
    def run(self):

        self.main_date = dt.today()
        loop = True
        # main loop
        while loop:
            print(main_menu)
            user_input: str = input()
            if user_input == "q":
                self.quit()
            elif user_input.startswith("cal"):
                arg = user_input[3:]
                if arg.startswith(":"):
                    self.main_date = dt.strptime(arg[1:], "%d/%m/%Y")
                elif arg.startswith("-"):
                    self.main_date -= timedelta(days=int(arg[1:]))
                elif arg.startswith("+"):
                    self.main_date += timedelta(days=int(arg[1:]))
                else:
                    self.main_date = dt.today()
                self.calendar()
            elif user_input.startswith("s"):
                self.select(user_input[1:])
            elif user_input == "new":
                self.new_reservation()
            elif user_input == "v":
                if all(Paiement.verify()):
                    print("Les données sont intégrales")
                else:
                    print("Les données ont été corrompues")

    def quit(self):
        """Quit the program"""
        sys.exit()

    def calendar(self, before=4, after=10):
        """Print calendar"""
        # improve: timedelta can be modify
        now = self.main_date
        start = now - timedelta(days=before)
        end = now + timedelta(days=after)
        query = get_stays_between(start, end)

        table = []

        date = start
        tmp_table = [""]  # ['', 18/01, 19/01, etc..]
        while date < end:
            if date + timedelta(hours=1) >= dt.today() >= date - timedelta(hours=1):
                tmp_table.append("#####")
            else:
                tmp_table.append(date.strftime("%d/%m"))
            date += timedelta(days=1)
        table.append(tmp_table)

        tmp_table = []  # [101, 'Dupont', 'Dupont', etc..]
        for room in ROOMS:
            tmp_table.append(room)
            date = start
            while date < end:
                for stay in query:
                    if (
                        stay.room == room
                        and stay.check_in <= date
                        and stay.check_out > date
                    ):
                        tmp_table.append(stay.title())
                        break
                else:
                    tmp_table.append(" ")
                date += timedelta(days=1)
            table.append(tmp_table)
            tmp_table = []
        # table: [['', 18/01, 19/01, etc..], [101, Dupont, Dupont], [102, ...]]
        # print(table)
        print_table = Texttable(max_width=130)
        print_table.add_rows(table)
        print(print_table.draw())

    def select(self, args):
        room, date = args.split("-")
        tmp_date = date.split("/")
        if len(tmp_date) == 2:
            date += "/" + str(dt.today().year)
        elif len(tmp_date) == 3:
            pass
        else:
            return None
        date = dt.strptime(date, "%d/%m/%Y")

        query = Stay.select().where(
            (Stay.check_in < date + timedelta(hours=1))
            & (Stay.check_out > date)
            & (Stay.room == room)
        )
        assert len(list(query)) <= 1
        stay = list(query)[0]
        self._info_stay(stay)

    def _info_stay(self, stay: Stay, print_only=False):
        print(
            f"{stay.title()} - Du {stay.check_in.strftime('%d/%m')} au {stay.check_out.strftime('%d/%m')} ({(stay.check_out-stay.check_in).days} nuits)\nPrix: {stay.prices}\n{stay.notes}"
        )

        if print_only:
            return

        user_input: str = input(MESSAGE_IN_STAY_SELECTION)
        if user_input == "c":
            return
        elif user_input.isdigit():
            stay.room = int(user_input)
            stay.save()
            print(f"Le séjour est déplacé en {stay.room}")
        elif user_input == "c":
            user_input = input("Que modifier ? (1-6) ")
            value = input("Nouvelle Valeur ? ")
            if user_input == "1":
                stay.prices = value
            elif user_input == "2":
                stay.check_in = dt.strptime(value, "%d/%m/%Y")
            elif user_input == "3":
                stay.check_out = dt.strptime(value, "%d/%m/%Y")
            elif user_input == "4":
                stay.room = int(value)
            elif user_input == "5":
                stay.name = value
            elif user_input == "6":
                stay.notes = value
            stay.save()
        elif user_input == "r":
            self._info_reservation(stay.reservation)
        elif user_input == "p":
            self.info_payment(stay)

    def _info_reservation(self, reservation: Reservation, print_only=False):
        for n, stay in zip(range(len(reservation.stays)), reservation.stays):
            print(f"{n+1}: ")
            self._info_stay(stay, print_only=True)
            print("-" * 130)
        for achat in reservation.sales:
            print(
                f"{achat.date}: {achat.product.name} x{achat.quantity} = {achat.total_price()}"
            )
        paid = sum(map(lambda x: x.amount, reservation.paiements))
        print(
            f"Prix: {reservation.total_price()} - Payé: {paid} - Reste: {reservation.total_price() - float(paid)}"
        )

        if print_only:
            return

        user_input = input(
            "d{n} - Séparer le séjour n dans une nouvelle réservation\ns{n} - Selectionner le séjour n\na - Achat produit\nc - Cancel\n"
        )
        if user_input.startswith("d"):
            n = int(user_input[1:])
            if len(reservation.stays) > 1:
                res = Reservation()
                res.save()
                reservation.stays[n - 1].reservation = res
                reservation.stays[n - 1].save()
            else:
                print("Inutile")
        elif user_input.startswith("s"):
            n = int(user_input[1:])
            self._info_stay(reservation.stays[n - 1])
        elif user_input == "a":
            self.achat(reservation)

    def new_reservation(self):
        name = input("Nom: ")
        check_in = dt.strptime(input("check-in: ") + "/2018", "%d/%m/%Y")
        check_out = dt.strptime(input("check-out: ") + "/2018", "%d/%m/%Y")
        room = int(input("Chambre: "))
        price = input("prix: ")
        notes = input("Notes: ")
        insert_new(name, check_in, check_out, room, price, notes)

    def info_payment(self, stay: Stay):
        self._info_reservation(stay.reservation, print_only=True)
        print("Paiements actuels:")
        if not stay.reservation.paiements:
            print("AUCUN")
        for pay in stay.reservation.paiements:
            print(f"{pay.date}: {pay.amount}€ - {pay.get_pay_method()} - {pay.notes}")
        amount = input("Montant (c - cancel): ")
        if amount == "c":
            return
        else:
            amount = int(amount)
        date = input("date (vide si aujourd'hui, dd/mm/yyyy): ")
        method = int(input(MESSAGE_IN_PAYMENT + ": "))
        notes = input("Notes: ")
        if not date:
            date = dt.today()
        else:
            date = dt.strptime(date, "%d/%m/%Y")
        payment(stay.reservation, date, amount, PaymentMethod(method), notes)

    def achat(self, res):
        print("Produit:")
        for product in Product.select():
            print(product.name, product.initial_price)
        user_input = input("Numéro produit (commence à 1): ")
        sell_product(Product.get(id=int(user_input)), in_res=res)


if __name__ == "__main__":
    # PMS_CLI().run()
    pass
