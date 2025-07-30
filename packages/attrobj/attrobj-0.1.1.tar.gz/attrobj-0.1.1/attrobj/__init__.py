"""
A dictionary manipulator that enables attribute-style access to dictionary items.

Also, supports nested dictionaries.
"""

from typing import Any, Callable, Iterable, TypeAlias

iterable = lambda x: hasattr(x, '__iter__') and\
    not isinstance(x, (str, bytes, dict))
NoneType = type(None)
Predicate: TypeAlias = Callable[[Any], bool]

class Object(dict):
    """
    A dictionary subclass that enables attribute-style access to dictionary items.
    
    The Object class extends dict to provide dual access to its contents through both
    square bracket notation (obj['key']) and dot notation (obj.key). It also includes
    special handling for nested dictionaries and iterables.
    
    Features:
        - Attribute-style access to dictionary keys
        - Automatic conversion of nested dictionaries to Object instances
        - List conversion for iterables containing dictionaries
        - Utility methods for filtering and querying content
    
    Examples:
        >>> obj = Object({"name": "John", "details": {"age": 30}})
        >>> print(obj.name)  # Outputs: "John"
        >>> print(obj.details.age)  # Outputs: 30
        >>> obj.skills = ["python", "javascript"]
        >>> print(obj)  # Outputs: Object({'name': 'John', 'details': {'age': 30}, 'skills': ['python', 'javascript']})
        >>> print(obj.haskey("name"))  # Outputs: True
        >>> print(obj.only(is_not=str))  # Outputs: Object with non-string values
    
    Note:
        Attribute access first checks dictionary keys before falling back to normal attributes.
        Not recommended as a base class for inheritance due to its attribute access behavior.
    """
    def __str__(self) -> str:
        """Returns a string representation of the object."""
        return f"Object({dict(self)})"
    
    def __getattribute__(self, name: str):
        """
        Customizes attribute access for dictionary-like objects.

        ## Args:
            name (str): The name of the attribute being accessed.

        ## Returns:
            Any: The value associated with the attribute name if it exists as a key,
             otherwise the result of default attribute lookup.

        ## Example:
            >>> obj = DictLikeClass()
            >>> obj['foo'] = 'bar'
            >>> obj.foo  # Returns 'bar' through __getattribute__
        
        ## Note:
            - This method allows accessing dictionary keys as attributes.
            - Please do not inherit from this class, as it may lead to exceptions.
        """

        if name in self:
            val = self[name]
            if iterable(val):
                if val and isinstance(val[0], dict):
                    return list(map(Object, val))
                return val
            return val if not isinstance(val, dict) else Object(val)
        return super().__getattribute__(name)
    
    def __setattr__(self, name: str, value) -> None:
        """
        Override the attribute setting behavior to store attributes in the dictionary.

        This method allows setting attributes using dot notation, which are then stored
        in the underlying dictionary.

        ## Args:
            name (str): The name of the attribute to set
            value (Any): The value to assign to the attribute

        ## Returns:
            None

        ## Example:
            >>> obj = ClassName()
            >>> obj.new_attr = 123  # Sets obj['new_attr'] = 123
        """
        self[name] = value
    
    def __getitem__(self, key):
        return self.get(key)
    
    def any(self, keys: Iterable[str], key: bool = False) -> Any |  None:
        """
        Find the first key in the provided iterable that exists in the object and return its value.

        ## Args:
            keys (Iterable[str]): An iterable of keys to check for existence.
            key (bool, optional): If True, returns the key-value pair as an Object. Defaults to False.

        ## Returns:
            Any | Object | None: The value of the first found key, an Object containing the key-value pair
                               if key=True, or None if no keys are found.
        """
        retv = map(lambda key: (key, self.get(key)), keys)
        vals = next(filter(lambda r: r[1] is not None, retv), None)
        if vals is not None:
            if key:
                return Object({vals[0]: vals[1]})
            return vals[1]
        return None

    def haskey(self, key: str) -> bool:
        """
        Check if the object has a specific key.

        ## Args:
            key (str): The key to check for existence.

        ## Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self
    
    def only(self, predicate: Predicate = None, is_not: type = NoneType):
        """
        Filter the object to only include keys that match the predicate.

        ## Args:
            predicate (str): The key to filter by.

        ## Returns:
            Object: A new Object containing only the key-value pairs that match the predicate.
        """
        return Object({
            k: v for k, v in self.items()
            if (predicate(k, v) if predicate else not isinstance(v, is_not))
        })
