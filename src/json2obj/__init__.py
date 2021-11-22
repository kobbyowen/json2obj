""" Attribute access """

import json
from typing import Union, Any
from datetime import datetime
from pprint import pprint
import copy


class JSONObjectMapper:
    """Used to convert json to python objects that can be queried and set using the member access(.) operator."""

    def __init__(self, data: Union[str, bytes, bytearray, dict], readonly: bool = False) -> None:
        """Initializes the object with  JSON data. If readonly is False, addition of new attributes and changing of values will throw an AttributeError

        Args:
            data: Union[str, bytes, bytearray, dict]: The JSON data 
            readonly: bool: Whether to prevent setting attributes or addition of new attributes or not 
        """
        if isinstance(data, bytearray):
            data = bytes(data).decode()
        elif isinstance(data, bytes):
            data = data.decode()
        else:
            assert isinstance(data, (str, dict))

        is_dict = isinstance(data, dict)
        self.__data = json.dumps(data) if is_dict else data
        self.__json = data if is_dict else json.loads(self.__data)
        self.__readonly = readonly

    def __getattr__(self, name: str) -> Any:
        """Used to control attributes access"""

        if name in ["_JSONObjectMapper__data", "_JSONObjectMapper__json", "_JSONObjectMapper__readonly"]:
            return object.__getattribute__(self, name)
        if name not in self.__json:
            raise AttributeError(f'{name} cannot be found')
        value = self.__json[name]
        if isinstance(value, dict):
            return self.__class__(value, self.__readonly)
        return copy.copy(value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Used to control attribute assignment. Always fails if readonly is set to True"""

        if name in ["_JSONObjectMapper__data", "_JSONObjectMapper__json", "_JSONObjectMapper__readonly"]:
            return object.__setattr__(self, name, value)

        if self.__readonly:
            raise AttributeError(f'value of {name!r} cannot be changed')

        value = self._convert_to_json_value(value)
        self.__json[name] = value

    def __contains__(self, key: Any) -> bool:
        """ Check if a key exists on object. it only check top level keys"""

        return key in self.__json

    def _convert_to_json_value(self, value: Any) -> Any:
        """Converts a value to a JSON value

        Args:
            value (Any): The value to convert

        Returns:
            Any: The value to return
        """
        if isinstance(value, self.__class__):
            return str(value)
        if isinstance(value, (str, int, dict, list)):
            return value
        if isinstance(value, datetime):
            return str(value)
        raise ValueError(f'{value} is not a valid JSON literal')

    def __str__(self):
        """ Get the string representation of the updated JSON object"""
        return json.dumps(self.__json)

    def to_dict(self):
        """ Get the dictionary representation of the JSON object"""

        return self.__json

    def __repr__(self):
        """ Same as __str__ """
        return self.__str__()


if __name__ == '__main__':

    person = JSONObjectMapper("""{
        "name" : "trumpowen" , 
        "age" : 125 
    }""")

    assert person.name == "trumpowen"
    assert person.age == 125

    # replaces and overwrites
    person.name = {}
    person.name.first_name = "Wilkins"
    person.name.last_name = "Owen"
    person.name.other_names = ["Trump"]
    person.dob = datetime(1900, 12, 6)

    assert person.name.first_name == "Wilkins"
    assert person.name.last_name == "Owen"
    assert person.name.other_names == ["Trump"]

    person.name.parent_names = {
        "mother": {
            "first_name": "Coding",
            "last_name": "Guru",
            "other_names": []
        },
        "father": {
            "first_name": "Python",
            "last_name": "Snake",
            "other_names": []
        }
    }

    assert person.name.parent_names.mother.first_name == "Coding"
    assert person.name.parent_names.mother.other_names == []

    try:
        person.name.unknown
    except AttributeError:
        assert True
    else:
        assert False
