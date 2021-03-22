from django.db.models.query import QuerySet
from .get import deep_get

class CSV:
    quotation = "\""
    antiquotation = "\"\""
    array_delimiter = "//"
    vertical_delimiter = "\n"
    horizontal_delimiter = ";"

    def __init__(self, headers, data, arrays_newline=False):
        self.data = data
        self.add = headers.get("$add$")

        if self.add:
            del headers["$add$"]

        self.headers = headers
        self.arrays_newline = arrays_newline

    def _transform_header_defaults(self, header):
        if type(header) == dict:
            return header["default"]

        return None

    def _transform_header_texts(self, header):
        if type(header) == dict:
            return header["name"]

        return header

    def generate(self):
        add_keys = self.add.keys() if self.add else []
        text_add = tuple(map(lambda h: self.quotation + h + self.quotation, add_keys))
        add_len = len(add_keys)

        header_keys = self.headers.keys()
        header_len = len(header_keys)
        header_values = self.headers.values()

        text_headers = tuple(
            map(
                lambda h: self.quotation + self._transform_header_texts(h) + self.quotation,
                header_values
            )
        )

        default_headers = tuple(map(self._transform_header_defaults, header_values))

        string = self.horizontal_delimiter.join(text_headers) + (self.horizontal_delimiter if add_len > 0 else "")
        string += self.horizontal_delimiter.join(text_add) + self.vertical_delimiter

        for obj in self.data:
            index = 0
            add_index = 0

            for header in header_keys:
                value = deep_get(obj, header)

                if type(value) == list or type(value) == tuple or isinstance(value, QuerySet):
                    if self.arrays_newline:
                        value = self.vertical_delimiter.join(value)
                    else:
                        value = self.array_delimiter.join(value)

                if type(value) == bool:
                    value = 1 if value else 0

                if value == None:
                    value = default_headers[index] or ""

                value = str(value)
                value = value.replace(self.quotation, self.antiquotation)
                value = self.quotation + value + self.quotation

                string += value
                string += self.horizontal_delimiter if add_len > 0 or index < header_len - 1 else ""
                index += 1

            for key in add_keys:
                value = self.add[key]

                if type(value) == list or type(value) == tuple or isinstance(value, QuerySet):
                    if self.arrays_newline:
                        value = self.vertical_delimiter.join(value)
                    else:
                        value = self.array_delimiter.join(value)

                if type(value) == bool:
                    value = 1 if value else 0

                if value == None:
                    value = ""

                value = self.quotation + str(value) + self.quotation
                string += value

                if add_index < add_len - 1:
                    string += self.horizontal_delimiter

                add_index += 1

            string += self.vertical_delimiter

        return string
