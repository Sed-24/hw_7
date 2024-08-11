from collections import UserDict
from datetime import datetime, timedelta, date
from typing import Callable


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if len(value) > 0:
            super().__init__(value)


class Phone(Field):
    def __init__(self, value: str):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError


class Birthday(Field):

    def get_days_from_today(self, date):
        data_editing = ''
        for i in date:
            if i in '1234567890':
                data_editing += i
            else:
                data_editing += ''
        try:
            date_string = datetime.strptime(data_editing, '%d.%m.%Y').date()
            today = datetime.today().date()
            return (today - date_string).days
        except ValueError:
            return 'Невірно введена дата'

    def date_to_string(self, data):
        return data.strftime('%d.%m.%Y')

    def __str__(self) -> str:
        return self.date_to_string(date)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)

    def edit_phone(self, old_phone, new_phone):
        for ph in self.phones:
            if ph.value == old_phone:
                if len(new_phone) == 10 and new_phone.isdigit():
                    ph.value = new_phone
                    break
        else:
            raise ValueError

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, note):
        self.data[note.name.value] = note

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def find_next_weekday(self, one_date: datetime, weekday: int):
        result_day = weekday - one_date.weekday()

        if result_day <= 0:
            result_day += 7

        return one_date + timedelta(result_day)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, users, days=7):
        upcoming_birthdays = []
        today = date.today()

        for user in users:
            birthday_this_year = user["birthday"].replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = self.adjust_for_weekend(user["birthday"].replace(year=today.year + 1))
            if 0 <= (birthday_this_year - today).days <= 7:
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)

                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append({"name": user["name"], "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self):
        return f"Contacts book: name: {'; '.join(p for p in self.data)}"


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Give me name and phone please."
        except KeyError:
            return "Specify the correct search parameter"
    return inner


@input_error
def main():
    book = AddressBook()
    print("Welcome to the assistant bot Fox!")
    while True:

        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif "hello" == command:
            print("How can I help you?")
        elif "add" == command:
            print(add_contact(*args, book))
        elif "change" == command:
            print(change_contact(*args, book))
        elif "phone" == command:
            print(show_phone(*args, book))
        elif "all" == command:
            print(show_all(), book)
        elif "add-birthday" == command:
            print(add_birthday(args, book))
        elif "show-birthday" == command:
            print(show_birthday(args, book))
        elif "birthdays" == command:
            print(birthdays(book))
        else:
            print("Invalid command.")


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(*add):
    if add[0] in contact:
        return "The contact already exists"
    else:
        contact[add[0]] = add[1]
        return "Contact added."


@input_error
def change_contact(*change):
    if change[0] in contact:
        contact[change[0]] = change[1]
        return "Contact updated."
    else:
        return "Contact not found"


def show_phone(*phone):
    if phone[0] in contact:
        return contact[phone[0]]
    else:
        return "Contact not found"


@input_error
def show_all():
    if len(contact) > 0:
        return contact
    return 'The phone book is empty'


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    book.find(name).add_birthday(birthday)
    return 'Birthday added.'


@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
    return str(book.find(args[0]).birthday)


@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


if __name__ == "__main__":
    contact = {}
    main()

