import dataclasses
import json
from pathlib import Path

import restorify.utils as _u


__classes_map = {}
def restorable(cls):
    cls = _jsonable(cls)
    cls.dump = _dump_object
    cls.load = classmethod(lambda c, p: c.from_json( _u.read_text(p)) )
    __classes_map[cls.__name__] = cls
    return cls

def restore(param: any, cls = None) -> object:
    if cls: 
        if isinstance(param, Path):
            return cls.load(param)
        else:
            return _from_object(cls, json.loads(param) )
    else:
        return _get_object(param)
    
def _get_object(where_from: Path) -> object:
    file_name  = where_from.parts[-1].split('.')[0]
    class_name = _u.snake_to_camel(file_name)
    if class_name not in __classes_map:
        return None
    cls = __classes_map[class_name]
    return cls.load(where_from)
 
def _dump_object(self, where: Path):
    d = self.to_dict()
    _u.write_json(d, where.joinpath(self.json_name))


def _jsonable(cls):
    cls = _dictable(cls)
    cls.to_json = _to_json
    cls.from_json = classmethod(_from_json)
    cls.json_name =  _u.camel_to_snake(cls.__name__) + ".json"
    return cls

def _dictable(cls):
    cls.to_dict = _to_dict
    cls.from_dict = classmethod(_from_dict)
    return cls


def _to_json(self):
    return json.dumps(_to_dict(self), indent=4)

def _from_json(cls, j: str):
    return _from_dict( cls, json.loads(j) )

def _to_dict(self):
    if dataclasses.is_dataclass(self):
        return dataclasses.asdict(self)
    return vars(self)

def _from_dict(cls, val: dict):
    return _from_object(cls, val)

def _from_object(cls, val: object):
    try:
        ann =  cls.__annotations__
        d = {}
        for k,v in ann.items():
            e = _from_object(v, val[k])
            d[k] = e
        return cls(**d) #is dataclass?
    except:
        (...)

    try:
        type_of_list_element = cls.__args__[0]
        l = [ _from_object(type_of_list_element, x) for x in val ]
        return cls(l)
    except:
        (...)

    try:
        type_of_dict_key, type_of_dict_val = cls.__args__
        return cls({ _from_object(type_of_dict_key, k):_from_object(type_of_dict_val, v) for k,v in val.items() })
    except:
        (...)

    try:
        return cls(val)
    except:
        (...)

    raise TypeError(f"Cannot create class of type {cls.__name__} with value {str(val)}.")
