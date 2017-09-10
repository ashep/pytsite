"""PytSite Abstract Cache Driver
"""
from typing import Any as _Any, Mapping as _Mapping, List as _List
from abc import ABC as _ABC, abstractmethod as _abstractmethod

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Abstract(_ABC):
    """Abstract Cache Driver
    """

    def __init__(self, name: str):
        """Init
        """
        # Pool's name
        self._name = name

    @property
    def name(self) -> str:
        """Get pool's name
        """
        return self._name

    @_abstractmethod
    def has(self, key: str) -> bool:
        """Check whether an item exists in the pool
        """
        pass

    @_abstractmethod
    def put(self, key: str, value: _Any, ttl: int = None) -> _Any:
        """Put an item into the pool
        """
        pass

    @_abstractmethod
    def get(self, key: str) -> _Any:
        """Get an item from the pool
        """
        pass

    @_abstractmethod
    def put_hash(self, key: str, value: _Mapping, ttl: int = None) -> _Any:
        """Put a hash-like item into the pool
        """
        pass

    @_abstractmethod
    def put_hash_item(self, key: str, hash_key: str, value: _Any) -> _Any:
        """Put a value into a hash-like item
        """
        pass

    @_abstractmethod
    def get_hash(self, key: str, hash_keys: _List[str] = None) -> _Mapping:
        """Get a hash-like item from the pool
        """
        pass

    @_abstractmethod
    def get_hash_item(self, key: str, hash_key: str) -> _Any:
        """Get a value for a key from a hash-like item
        """
        pass

    @_abstractmethod
    def ttl(self, key: str) -> int:
        """Get key's expiration time
        """
        pass

    @_abstractmethod
    def rnm(self, key: str, new_key: str):
        """Rename a key
        """
        pass

    @_abstractmethod
    def rm(self, key: str):
        """Remove a single item from the pool
        """
        pass

    @_abstractmethod
    def clear(self):
        """Clear entire pool
        """
        pass

    @_abstractmethod
    def cleanup(self):
        """Cleanup outdated items from the cache
        """
        pass
