## json2obj

Allows you to transform JSON data into an object whose members can be queried using the member access operator. Unlike `json.dumps` in the standard library that returns a dictionary object, this library returns a JSONObjectMapper object. The attributes of these objects are defined by the contents of the JSON data provided to it

## Examples

```python

import datetime
from json2obj import JSONObjectMapper

person = JSONObjectMapper("""{
        "name" : "trumpowen" ,
        "age" : 125
    }""")

person.name == "trumpowen"  # true
person.age == 125           # true

 # replaces and overwrites
person.name = {}
person.name.first_name = "Wilkins"
person.name.last_name = "Owen"
person.name.other_names = ["Trump"]

# add new attribute. If this is not desired, you can initialize the object with readonly set to True. This will prevent the addition of new attributes and changing the values of existing attributes
person.dob = datetime(1900, 12, 6)

json_data = str(person) # returns a string representation
json_as_dict = person.to_dict() # returns a dictionary representation


```

## Documentation

Use `help(obj)` , where obj is an instance of JSONObjectMapper
