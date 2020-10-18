# Write your code here
from random import randint
import sqlite3

#global card number for session
gcard = 0

class BankingSystem:
    def __init__(self):
        self.logged_in = False
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()
        self.menu()

# create table
    def create_table(self):
        sql_create_card_table = """CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT,
        pin TEXT, balance INTEGER DEFAULT 0) """
        self.cur.execute(sql_create_card_table)
        self.conn.commit()

# add card in table
    def create_card(self, id_, number, pin, balance):
        sql_insert_card = """INSERT INTO card (id, number, pin, balance) VALUES (?, ?, ?, ?) """
        data_tuple = (id_, number, pin, balance)
        self.cur.execute(sql_insert_card, data_tuple)
        self.conn.commit()

# depositing cash to the card
    def add_cash(self, cash, num):
        sql_update_balance = """UPDATE card SET balance = (balance + ?) WHERE number = ?"""
        data_tuple = (cash, num)
        self.cur.execute(sql_update_balance, data_tuple)
        self.conn.commit()

# getting the card balance
    def my_balance(self, num):
        sql_my_balance_query = """SELECT balance FROM card WHERE number = ?"""
        data_tuple = (num,)
        self.cur.execute(sql_my_balance_query, data_tuple)
        money = self.cur.fetchone()[0]
        return money


    def gen_id(self):
        query = """SELECT id FROM card ORDER BY id DESC LIMIT 1"""
        self.cur.execute(query)
        records = self.cur.fetchall()
        try:
            return records[0][0] + 1
        except IndexError:
            return 1

# search card in DB
    def read_card(self, card, pin):
        query = """SELECT number, pin FROM card WHERE number = ? AND pin = ?"""
        data_tuple = (card, pin)
        self.cur.execute(query, data_tuple)
        rows = self.cur.fetchone()
        return rows

# main menu
    def menu(self):
        while not self.logged_in:
            print('1. Create an account\n2. Log into account\n0. Exit')
            choice = input()
            if choice == '1':
                self.create()
            elif choice == '2':
                self.login()
            elif choice == '0':
                print('\nBye!')
                self.cur.close()
                self.conn.close()
                quit()
            else:
                print('Unknown option.\n')

# account of the cardholder
    def account_menu(self):
        while self.logged_in:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input()
            if choice == '1':
                num = gcard
                money = self.my_balance(num)
                print('\nBalance: ', money)
            elif choice == '2':
                cash = int(input('\nEnter income:'))
                num = gcard
                self.add_cash(cash, num)
                print('\nIncome was added!\n')
            elif choice == '3':
                print("Transfer\nEnter card number:")
                transfer_card = input()
                if int(transfer_card) == int(gcard):
                        print("You can't transfer money to the same account!")
                else:
                    check_transfer_card = self.check_card(transfer_card)
                    if check_transfer_card:
                        print("Enter how much money you want to transfer:")
                        to_transfer = input()
                        balance_check = self.cur.execute(f'SELECT balance FROM card WHERE number = {gcard}').fetchone()
                        balance_check = ''.join(map(str, balance_check))
                        if int(to_transfer) > int(balance_check):
                            print("Not enough money!")
                        else:
                            print("Success!")
                            self.cur.execute(f'UPDATE card SET balance = balance - {to_transfer} WHERE number = {gcard}')
                            self.cur.execute(f'UPDATE card SET balance = balance + {to_transfer} WHERE number = {transfer_card}')
                            self.conn.commit()
                    else:
                        print("Such a card does not exist.")
            elif choice == '4':
                print('The account has been closed!')
                self.delete_card()
            elif choice == '5':
                self.logged_in = False
                print('\nYou have successfully logged out!\n')
            elif choice == '0':
                print('\nBye!')
                self.cur.close()
                self.conn.close()
                quit()
            else:
                print('Unknown option.\n')

# generating a card number/PIN
    def create(self):
        print()
        id_ = self.gen_id()
        card = self.luhn_alg()
        pin = str.zfill(str(randint(0000, 9999)), 4)
        self.create_card(id_, card, pin, 0)
        print(f'Your card has been created\nYour card number:\n{card}\nYour card PIN:\n{pin}\n')

# login to account
    def login(self):
        print('\nEnter your card number:')
        card = input()
        global gcard
        gcard = card
        print('Enter your PIN:')
        pin = input()
        cards = self.read_card(card, pin)
        if cards:
            print('\nYou have successfully logged in!\n')
            self.logged_in = True
            self.account_menu()
        else:
            print('\nWrong card number or Pin!\n')

# checking the card number by the Luhn algorithm (generating card)
    def luhn_alg(self):
        card = '400000' + str.zfill(str(randint(000000000, 999999999)), 9)
        card_check = [int(i) for i in card]
        for index, _ in enumerate(card_check):
            if index % 2 == 0:
                card_check[index] *= 2
            if card_check[index] > 9:
                card_check[index] -= 9
        check_sum = str((10 - sum(card_check) % 10) % 10)
        card += check_sum
        return card

# checking the card number for transfer
    def check_card(self, transfer_card):
        c = [int(x) for x in transfer_card[::-2]]
        u2 = [(2*int(y))//10+(2*int(y))%10 for y in transfer_card[-2::-2]]
        check = sum(c+u2)%10
        if check == 0:
            query = """SELECT number FROM card WHERE number = ?"""
            data_tuple = (transfer_card,)
            self.cur.execute(query, data_tuple)
            numbs = self.cur.fetchone()
            return numbs
        elif check > 0:
            print('Probably you made mistake in the card number. Please try again!')

# close of account
    def delete_card(self):
        sql_delete_card = """DELETE FROM card WHERE number = ?"""
        data_tuple = (gcard,)
        self.cur.execute(sql_delete_card, data_tuple)
        self.conn.commit()

BankingSystem().menu()

