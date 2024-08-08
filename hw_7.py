from collections import UserDict
from datetime import datetime, timedelta
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
    format: str = '%d.%m.%Y'

    def __init__(self, value: str):
        try:
            self.value = datetime.strptime(value, self.format)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self) -> str:
        return self.value.strftime(self.format) if self.value else 'Not specified'


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

    def date_to_string(self, date: datetime):
        return date.strftime(Birthday.format)

    def find_next_weekday(self, one_date: datetime, weekday: int):
        result_day = weekday - one_date.weekday()

        if result_day <= 0:
            result_day += 7

        return one_date + timedelta(result_day)

    def adjust_for_weekend(self, day_cl, birthday: datetime) -> datetime:
        if birthday.weekday() >= 5:
            return day_cl.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days: int = 7):
        dates = self.data[str, list[str]] = {}
        today = datetime.today()

        for name, record in self.data.items():
            if record.birthday:
                # Birthday this year.
                reality = record.birthday.value.replace(today.year)

                if reality < today:
                    reality = reality.replace(today.year + 1)

                if 0 <= (reality - today).days <= days:
                    # Birthday date.
                    event = self.date_to_string(self.adjust_for_weekend(reality))

                    if event not in dates:
                        dates[event] = []
                    dates[event].append(name)
        return dates

    def __str__(self):
        return f"Contacts book: name: {'; '.join(p for p in self.data)}"


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        command, *args = parse_input(input("Enter a command: "))

        match command:
            case 'hello':
                print('How can I help you?')
            case 'add':
                print(add_contact(args, book))
            case 'change':
                print(change_contact(args, book))
            case 'phone':
                print(show_phone(args, book))
            case 'all':
                print(show_all(book))
            case 'add-birthday':
                print(add_birthday(args, book))
            case 'show-birthday':
                print(show_birthday(args, book))
            case 'birthdays':
                print(birthdays(book))
            case _ if command in ['close', 'exit']:
                print('Good bye!')
                break
            case _:
                print('Invalid command.')


def input_error(func: Callable):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return 'Something went wrong.'


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
