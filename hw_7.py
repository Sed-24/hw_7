from collections import UserDict
from datetime import datetime, timedelta, date


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
    FORMAT: str = '%d.%m.%Y'

    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, self.FORMAT)
        except ValueError:
            raise 'BirthdayError'

    def __str__(self):
        return self.value.strftime(self.FORMAT) if self.value else 'Not find'


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

    def edit_phone(self, old, new):
        for ph in self.phones:
            if ph != new:
                self.phones[self.phones.index(ph)] = Phone(new)
                return
            return self.phones[old]

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

    def date_to_string(self, date):
        return date.strftime(Birthday.FORMAT)

    def find_next_weekday(self, start_date, weekday) -> datetime:
        days_ahead = weekday - start_date.weekday()

        if days_ahead <= 0:
            days_ahead += 7

        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days: int = 7):
        dates = {}
        today = datetime.today()

        for name, record in self.data.items():
            if record.birthday:
                # Birthday this year.
                real = record.birthday.value.replace(year=today.year)
                if real < today:
                    real = real.replace(year=today.year + 1)

                if 0 <= (real - today).days <= days:
                    # Congratulation date.
                    event = self.date_to_string(self.adjust_for_weekend(real))
                    if event not in dates:
                        dates[event] = []
                    dates[event].append(name)
        return dates

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
        except AttributeError:
            return 'Object has no attribute'
    return inner


@input_error
def main():
    book = AddressBook()
    print("Welcome to the assistant bot Fox!")
    while True:

        command, *args = parse_input(input("Enter a command: "))

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif "hello" == command:
            print("How can I help you?")
        elif "add" == command:
            print(add_contact(args, book))
        elif "change" == command:
            print(change_contact(args, book))
        elif "phone" == command:
            print(show_phone(args, book))
        elif "all" == command:
            print(*show_all(book))
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
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, phone_old, phone_new, *_ = args
    record = book.find(name)
    record.edit_phone(phone_old, phone_new)

    return 'Contact updated.'


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    return book.find(name)


@input_error
def show_all(book: AddressBook):
    return {book.find(name) for name in book}


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    book.find(name).add_birthday(birthday)
    return 'Birthday added.'


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    return book.find(name).birthday


@input_error
def birthdays(book: AddressBook):
    return {date_birthday: ', '.join(names) for date_birthday, names in book.get_upcoming_birthdays()}


if __name__ == "__main__":
    contact = {}
    main()
