import re
import datetime


class FieldType:
    pass


class DateTime(FieldType):
    datatype = str
    re_exp = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")

    @classmethod
    def parse(cls, data):
        m = cls.re_exp.match(data)
        if not m:
            raise ValueError("Does not match datetime format")

        return datetime.datetime.strptime(data, "%Y-%M-%d")
