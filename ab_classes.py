from collections import UserDict
from collections.abc import Iterator
from datetime import datetime, timedelta
import re
import json


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self) -> str:
        return str(self)

class Name(Field):
    def __str__(self):
        return super().__str__()


class Phone(Field):
    ...
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, nv):
        if nv.isdigit() and (len(nv) == 10 or len(nv) == 11 or len(nv) == 12):
            self.__value = nv
        else:
            raise ValueError("Phone number must have a proper length and consist only of digits")

    def __str__(self):
        return self.value




class Birthday(Field):

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, nv):
        input_date_true = r"\d{1,2}\.\d{1,2}\.\d{4}"
        if nv:
            if re.match(input_date_true, nv):
                self.__value = nv
            else:
                raise ValueError("Invalid birthday! Please input in format d.m.y")
        elif nv == None:
            self.__value = None
        


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        self.birthday = birthday
        if phone:
            self.phones.append(phone)


    def add_phone(self, phone: Phone):
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)
            
            return f'phone {phone} add to {self.name}'
        return f'{phone} already exist in {self.name}`s phones'
    
    def __str__(self) -> str:
        return f'{self.name}: {", ".join(str(p) for p in self.phones)}; Birthday: {self.birthday}'

    def change_phone(self, old_phone: Phone, new_phone: Phone):
        if str(new_phone) in self.phones:
            return f'{new_phone} already exists in {self.name}`s phones'
        else:
            for idx, ph in enumerate(self.phones):
                if str(old_phone) == ph:
                    self.phones[idx] = str(new_phone)
                    return f"{self.name}`s {old_phone} changed to {new_phone}"
            return f'{old_phone} not in {self.name}`s phones'

    def days_to_birthday(self, name: str):
        if self.birthday is None:
            return f"{name}'s birthday is unknown."
        else:
            today = datetime.now().date()
            birth = datetime.strptime(str(self.birthday), "%d.%m.%Y").date()
            
            next_birthday = datetime(today.year, birth.month, birth.day).date()
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth.month, birth.day).date()
            timedelta = next_birthday - today
            if timedelta.days == 0:
                return f"Today is {name}'s birthday!"
            elif timedelta.days == 1:
                return f"{name}'s birthday is tomorrow."
            else:
                return f"{name}'s birthday is in {timedelta.days} day(s)."
            
class AddressBook(UserDict):

    def __init__(self, N=1, filename="phone_book.json"):
        super().__init__()
        self.N = N
        self.filename = filename
        self.load_data()

    def add_record(self, record: Record):
        name_str = str(record.name)
        if name_str in self.data:
            existing_record = self.data[name_str]
            for phone in record.phones:
                existing_record.add_phone(phone)
        else:
            self.data[name_str] = record
        self.save_data()
        return f'Success!\nContact {record}'
    
    def load_data(self):
        try:
            with open(self.filename, 'r') as fb:
                data = json.load(fb)
                for name, record_data in data.items():
                    name_field = Name(name)
                    phones = []
                    for phone in record_data.get('phones'):
                        phones.append(phone)
                    # phones = [Phone(phone) for phone in record_data.get('phones')]
                    birthday_value = record_data.get('birthday', None)
                    birthday = Birthday(birthday_value) if birthday_value else None
                    record = Record(name_field, phones, birthday)
                    self.data[name] = record  
        except FileNotFoundError:
            with open(self.filename, 'w') as fb:
                json.dump({}, fb)

    def save_data(self):
        with open(self.filename, 'w') as fb:
            data = {str(name): {
                'phones': [str(phone) for phone in record.phones],
                'birthday': str(record.birthday) if record.birthday else None
            } for name, record in self.data.items()}
            json.dump(data, fb)

    def __str__(self) -> str:
        return '\n'.join(str(rec) for rec in self.data.values())
    
    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            self.save_data()
            return f"Record {name} deleted"
        return f"No record found with name {name}"
    
    def search(self, search_field):
            results = []
            for record in self.values():
                if isinstance(search_field, Name) and search_field.value.lower() in record.name.value.lower():
                    phones = ', '.join(str(phone) for phone in record.phones)
                    results.append(f"{record.name} : {phones}")
                elif isinstance(search_field, Phone) and any(search_field.value == phone.value for phone in record.phones):
                    results.append(f"{record.name} : {search_field.value}")
            if results:
                return '\n'.join(results)
            return "No matching records found."