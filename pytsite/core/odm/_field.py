"""ODM Fields.
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from abc import ABC as _ABC
from datetime import datetime as _datetime
from bson.objectid import ObjectId as _bson_ObjectID
from bson.dbref import DBRef as _bson_DBRef


class Abstract(_ABC):
    """Base field.
    """
    def __init__(self, name: str, default=None, not_empty: bool=False):
        """Init.
        :param not_empty:
        """
        self._name = name
        self._default = default
        self._not_empty = not_empty
        self._modified = False
        self._value = default

    def get_name(self):
        """Get name of the field.
        """
        return self._name

    def is_modified(self) -> bool:
        """Is the field has been modified?
        """
        return self._modified

    def reset_modified(self):
        """Reset the 'modified' status of the field.
        """
        self._modified = False
        return self

    def set_val(self, value, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        self._value = value
        if change_modified and not self._modified:
            self._modified = True
        return self

    def get_val(self, **kwargs):
        """Get value of the field.
        """
        return self._value

    def get_storable_val(self):
        """Get value suitable to store in a database.
        """
        if self._not_empty:
            if hasattr(self, '__len__') and not len(self._value):
                raise Exception("Value of the field '{}' cannot be empty.".format(self.get_name()))
            elif not self._value:
                raise Exception("Value of the field '{}' cannot be empty.".format(self.get_name()))

        return self._value

    def clear_val(self, reset_modified: bool=True, **kwargs):
        """Clears a value of the field.
        """
        raise Exception('Not implemented yet.')

    def add_val(self, value, change_modified: bool=True, **kwargs):
        """Add a value to the field.
        """
        raise Exception('Not implemented yet.')

    def subtract_val(self, value, change_modified: bool=True, **kwargs):
        """Remove a value from the field.
        """
        raise Exception('Not implemented yet.')

    def increment_val(self, change_modified: bool=True, **kwargs):
        """Increment a value of the field.
        """
        raise Exception('Not implemented yet.')

    def decrement_val(self, change_modified: bool=True, **kwargs):
        """Increment a value of the field.
        """
        raise Exception('Not implemented yet.')

    def delete(self):
        """Hook method to provide for the entity notification mechanism about its deletion.
        """
        pass

    def __str__(self) -> str:
        """Stringify field's value.
        """
        return str(self._value)


class ObjectId(Abstract):
    """ObjectId field.
    """
    def set_val(self, value, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, _bson_ObjectID):
            raise TypeError("ObjectId expected")

        return super().set_val(value, change_modified, **kwargs)


class List(Abstract):
    """List field.
    """
    def __init__(self, name: str, default=None, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)
        if self._value is None:
            self._value = []

    def set_val(self, value: list, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, list):
            value = [value]

        if not isinstance(value, list):
            raise TypeError("List expected")

        return super().set_val(value, change_modified, **kwargs)

    def add_val(self, value, change_modified: bool=True, **kwargs):
        """Add a value to the field.
        """
        allowed_types = (int, str, float, list, dict, tuple)

        valid = False
        for t in allowed_types:
            if isinstance(value, t):
                valid = True
                break

        if not valid:
            raise TypeError("Invalid value type: {}.".format(type(value)))

        self._value.append(value)

        if change_modified:
            self._modified = True

        return self

    def get_val(self, **kwargs) -> list:
        """Get value of the field.
        """
        return super().get_val(**kwargs)


class UniqueListField(List):
    """Unique List field.
    """

    def set_val(self, value: list, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        clean_val = []
        for v in value:
            if v and v not in clean_val:
                clean_val.append(v)

        super().set_val(clean_val, change_modified, **kwargs)
        return self

    def add_val(self, value, change_modified: bool=True, **kwargs):
        """Add a value to the field.
        """
        current_val = self.get_val()
        current_val.append(value)

        return self.set_val(current_val, change_modified, **kwargs)


class Dict(Abstract):
    """Dictionary field.
    """

    def __init__(self, name: str, default=None, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)
        if self._value is None:
            self._value = {}

    def set_val(self, value: dict, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, dict):
            raise TypeError("Field '{}': dictionary expected".format(self._name))

        return super().set_val(value, change_modified, **kwargs)


class Ref(Abstract):
    """DBRef Field.
    """

    def __init__(self, name: str, model: str, default=None, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)
        self._model = model

    def set_val(self, value, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        from ._model import ODMModel

        if isinstance(value, list) or isinstance(value, tuple):
            value = value[0] if len(value) else None

        if isinstance(value, _bson_DBRef) or value is None:
            pass
        elif isinstance(value, ODMModel):
            if value.model != self._model:
                raise ValueError("Instance of ODM model '{}' expected.".format(self._model))
            value = value.ref
        else:
            raise TypeError("Field '{}': entity or DBRef expected, but '{}' given.".format(self._name, str(value)))

        return super().set_val(value, change_modified, **kwargs)

    def get_val(self, **kwargs):
        """Get value of the field.
        """
        if isinstance(self._value, _bson_DBRef):
            from ._manager import get_by_ref
            referenced_entity = get_by_ref(self._value)
            if not referenced_entity:
                self.set_val(None)  # Updating field's value about missing entity
            return referenced_entity


class RefsListField(List):
    """List of DBRefs field.
    """

    def __init__(self, name: str, model: str, default=None, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)
        self._model = model

    def set_val(self, value: list, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, list):
            value = [list]

        clean_value = []
        from ._model import ODMModel
        for item in value:
            if isinstance(item, ODMModel):
                if item.model != self._model:
                    raise ValueError("Instance of ODM model '{}' expected.".format(self._model))
                clean_value.append(item.ref)
            elif isinstance(item, _bson_DBRef):
                clean_value.append(item)
            else:
                raise TypeError("List of DBRefs or entities expected.")

        return super().set_val(clean_value, change_modified, **kwargs)

    def get_val(self, **kwargs):
        """Get value of the field.
        """
        r = []
        for ref in self._value:
            from ._manager import get_by_ref
            entity = get_by_ref(ref)
            if entity:
                r.append(entity)

        return r

    def add_val(self, value, change_modified: bool=True, **kwargs):
        """Add a value to the field.
        """
        from ._model import ODMModel
        if not isinstance(value, _bson_DBRef) and not isinstance(value, ODMModel):
            raise TypeError("DBRef of entity expected.")

        if isinstance(value, _bson_DBRef):
            self._value.append(value)
        elif isinstance(value, ODMModel):
            self._value.append(value.ref)

        if change_modified:
            self._modified = True

        return self


class RefsUniqueList(RefsListField):
    """Unique list of DBRefs field.
    """

    def set_val(self, value: list, change_modified: bool=True, **kwargs):
        super().set_val(value, change_modified, **kwargs)
        clean_val = []
        ids = []
        for v in self.get_val():
            if v.id not in ids:
                clean_val.append(v)
                ids.append(v.id)
        return super().set_val(clean_val, change_modified, **kwargs)

    def add_val(self, value, change_modified: bool=True, **kwargs):
        super().add_val(value, change_modified, **kwargs)
        return self.set_val(self.get_val(**kwargs), change_modified, **kwargs)


class DateTime(Abstract):
    """Datetime field.
    """
    def __init__(self, name: str, default=_datetime(1970, 1, 1), not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)

    def set_val(self, value: _datetime, change_modified: bool=True, **kwargs):
        """Set field's value.
        """
        if not isinstance(value, _datetime):
            raise TypeError("DateTime expected")

        return super().set_val(value, change_modified, **kwargs)

    def get_val(self, fmt: str=None, **kwargs):
        """Get field's value.
        """
        value = super().get_val()
        """:type : _datetime"""

        if fmt:
            value = value.strftime(fmt)

        return value


class String(Abstract):
    """String field.
    """
    def __init__(self, name: str, default='', not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)

    def set_val(self, value: str, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        value = '' if value is None else str(value).strip()
        return super().set_val(value, change_modified, **kwargs)


class Integer(Abstract):
    """Integer field.
    """
    def __init__(self, name: str, default=0, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)

    def set_val(self, value: int, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, int):
            raise ValueError('Integer expected.')
        return super().set_val(int(value), change_modified, **kwargs)

    def add_val(self, value: int, change_modified: bool=True, **kwargs):
        """Add a value to the value of the field.
        """
        if not isinstance(value, int):
            raise ValueError('Integer expected.')
        return self.set_val(self.get_val(**kwargs) + value, change_modified, **kwargs)

class Float(Abstract):
    """Float field.
    """
    def __init__(self, name: str, default=0.0, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)

    def set_val(self, value: float, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        if not isinstance(value, float):
            raise ValueError('Float expected.')
        return super().set_val(value, change_modified, **kwargs)

    def add_val(self, value: float, change_modified: bool=True, **kwargs):
        """Add a value to the value of the field.
        """
        if not isinstance(value, float):
            raise ValueError('Float expected.')
        return self.set_val(self.get_val(**kwargs) + value, change_modified, **kwargs)



class Bool(Abstract):
    """Integer field.
    """

    def __init__(self, name: str, default=False, not_empty: bool=False):
        """Init.
        """
        super().__init__(name, default=default, not_empty=not_empty)

    def set_val(self, value: bool, change_modified: bool=True, **kwargs):
        """Set value of the field.
        """
        return super().set_val(bool(value), change_modified, **kwargs)


class StringsListField(List):
    pass


class Virtual(Abstract):
    pass
