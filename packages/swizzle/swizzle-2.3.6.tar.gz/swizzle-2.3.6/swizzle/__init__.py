# Copyright (c) 2024 Jan T. Müller <mail@jantmueller.com>

import builtins
import sys as _sys
import types
import unicodedata
from enum import EnumMeta
from functools import wraps
from importlib.metadata import version as get_version
from keyword import iskeyword as _iskeyword
from operator import itemgetter as _itemgetter

from .trie import Trie

try:
    from _collections import _tuplegetter
except ImportError:
    _tuplegetter = lambda index, doc: property(_itemgetter(index), doc=doc)


try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _version

    __version__ = _version("swizzle")
except PackageNotFoundError:
    try:
        from setuptools_scm import get_version

        __version__ = get_version(root=".", relative_to=__file__)
    except Exception:
        __version__ = "0.0.0-dev"

_type = builtins.type
MISSING = object()


def swizzledtuple(
    typename,
    field_names,
    *,
    rename=False,
    defaults=None,
    module=None,
    arrange_names=None,
    sep=None,
):
    """
    Create a custom named tuple class with swizzled attributes, allowing for rearranged field names
    and customized attribute access.

    This function generates a new subclass of `tuple` with named fields, similar to Python's
    `collections.namedtuple`. However, it extends the functionality by allowing field names to be
    rearranged, and attributes to be accessed with a customizable sep. The function also
    provides additional safeguards for field naming and attribute access.

    Args:
        typename (str): The name of the new named tuple type.
        field_names (sequence of str or str): A sequence of field names for the tuple. If given as
            a single string, it will be split into separate field names.
        rename (bool, optional): If True, invalid field names are automatically replaced with
            positional names. Defaults to False.
        defaults (sequence, optional): Default values for the fields. Defaults to None.
        module (str, optional): The module name in which the named tuple is defined. Defaults to
            the caller's module.
        arrange_names (sequence of str, optional): A sequence of field names indicating the order
            in which fields should be arranged in the resulting named tuple. This allows for fields
            to be rearranged and, unlike standard `namedtuple`, can include duplicates. Defaults
            to the order given in `field_names`.
        sep (str, optional): A separator string used to control how attribute names are constructed.
            If provided, fields will be joined using this separator to create compound attribute names.
            Defaults to None.

            Special case: If all field names have the same length `n` after optional renaming,
            and `sep` is still None, then `sep` is automatically set to `"+n"` (e.g. "+2").
            This indicates that names should be split every `n` characters for improved performance.

    Returns:
        type: A new subclass of `tuple` with named fields and customized attribute access.

    Notes:
        - The function is based on `collections.namedtuple` but with additional features such as
          field rearrangement and swizzled attribute access.
        - The `arrange_names` argument allows rearranging the field names, and it can include
          duplicates, which is not possible in a standard `namedtuple`.
        - The generated named tuple class includes methods like `_make`, `_replace`, `__repr__`,
          `_asdict`, and `__getnewargs__`, partially customized to handle the rearranged field order.
        - The `sep` argument enables a custom structure for attribute access, allowing for
          combined attribute names based on the provided sep. If no sep is provided,
          standard attribute access is used.

    Example:
        >>> Vector = swizzledtuple('Vector', 'x y z', arrange_names='y z x x')
        >>> # Test the swizzle
        >>> v = Vector(1, 2, 3)
        >>> print(v)  # Output: Vector(y=2, z=3, x=1, x=1)
        >>> print(v.yzx)  # Output: Vector(y=2, z=3, x=1)
        >>> print(v.yzx.xxzyzz)  # Output: Vector(x=1, x=1, z=3, y=2, z=3, z=3)
    """

    if isinstance(field_names, str):
        field_names = field_names.replace(",", " ").split()
    field_names = list(map(str, field_names))
    if arrange_names is not None:
        if isinstance(arrange_names, str):
            arrange_names = arrange_names.replace(",", " ").split()
        arrange_names = list(map(str, arrange_names))
        assert set(arrange_names) == set(
            field_names
        ), "Arrangement must contain all field names"
    else:
        arrange_names = field_names.copy()

    typename = _sys.intern(str(typename))

    _dir = dir(tuple) + [
        "__match_args__",
        "__module__",
        "__slots__",
        "_asdict",
        "_field_defaults",
        "_fields",
        "_make",
        "_replace",
    ]
    if rename:
        seen = set()
        name_newname = {}
        for index, name in enumerate(field_names):
            if (
                not name.isidentifier()
                or _iskeyword(name)
                or name in _dir
                or name in seen
            ):
                field_names[index] = f"_{index}"
            name_newname[name] = field_names[index]
            seen.add(name)
        for index, name in enumerate(arrange_names):
            arrange_names[index] = name_newname[name]

    for name in [typename] + field_names:
        if type(name) is not str:
            raise TypeError("Type names and field names must be strings")
        if not name.isidentifier():
            raise ValueError(
                "Type names and field names must be valid " f"identifiers: {name!r}"
            )
        if _iskeyword(name):
            raise ValueError(
                "Type names and field names cannot be a " f"keyword: {name!r}"
            )
    seen = set()
    for name in field_names:
        if name in _dir:
            raise ValueError(
                "Field names cannot be an attribute name which would shadow the namedtuple methods or attributes"
                f"{name!r}"
            )
        if name in seen:
            raise ValueError(f"Encountered duplicate field name: {name!r}")
        seen.add(name)

    arrange_indices = [field_names.index(name) for name in arrange_names]

    def tuple_new(cls, iterable):
        new = []
        _iterable = list(iterable)
        for index in arrange_indices:
            new.append(_iterable[index])
        return tuple.__new__(cls, new)

    field_defaults = {}
    if defaults is not None:
        defaults = tuple(defaults)
        if len(defaults) > len(field_names):
            raise TypeError("Got more default values than field names")
        field_defaults = dict(
            reversed(list(zip(reversed(field_names), reversed(defaults))))
        )

    field_names = tuple(map(_sys.intern, field_names))
    arrange_names = tuple(map(_sys.intern, arrange_names))
    num_fields = len(field_names)
    num_arrange_fields = len(arrange_names)
    arg_list = ", ".join(field_names)
    if num_fields == 1:
        arg_list += ","
    repr_fmt = "(" + ", ".join(f"{name}=%r" for name in arrange_names) + ")"
    _dict, _tuple, _len, _map, _zip = dict, tuple, len, map, zip

    namespace = {
        "_tuple_new": tuple_new,
        "__builtins__": {},
        "__name__": f"swizzledtuple_{typename}",
    }
    code = f"lambda _cls, {arg_list}: _tuple_new(_cls, ({arg_list}))"
    __new__ = eval(code, namespace)
    __new__.__name__ = "__new__"
    __new__.__doc__ = f"Create new instance of {typename}({arg_list})"
    if defaults is not None:
        __new__.__defaults__ = defaults

    @classmethod
    def _make(cls, iterable):
        result = tuple_new(cls, iterable)
        if _len(result) != num_arrange_fields:
            raise TypeError(
                f"Expected {num_arrange_fields} arguments, got {len(result)}"
            )
        return result

    _make.__func__.__doc__ = (
        f"Make a new {typename} object from a sequence " "or iterable"
    )

    def _replace(self, /, **kwds):
        def generator():
            for name in field_names:
                if name in kwds:
                    yield kwds.pop(name)
                else:
                    yield getattr(self, name)

        result = self._make(iter(generator()))
        if kwds:
            raise ValueError(f"Got unexpected field names: {list(kwds)!r}")
        return result

    _replace.__doc__ = (
        f"Return a new {typename} object replacing specified " "fields with new values"
    )

    def __repr__(self):
        "Return a nicely formatted representation string"
        return self.__class__.__name__ + repr_fmt % self

    def _asdict(self):
        "Return a new dict which maps field names to their values."
        return _dict(_zip(arrange_names, self))

    def __getnewargs__(self):
        "Return self as a plain tuple.  Used by copy and pickle."
        return _tuple(self)

    @swizzle_attributes_retriever(sep=sep, type=swizzledtuple, only_attrs=field_names)
    def __getattribute__(self, attr_name):
        return super(_tuple, self).__getattribute__(attr_name)

    def __getitem__(self, index):
        if not isinstance(index, slice):
            return _tuple.__getitem__(self, index)

        selected_indices = arrange_indices[index]
        selected_values = _tuple.__getitem__(self, index)

        seen = set()
        filtered = [
            (i, v, field_names[i])
            for i, v in zip(selected_indices, selected_values)
            if not (i in seen or seen.add(i))
        ]

        if filtered:
            _, filtered_values, filtered_names = zip(*filtered)
        else:
            filtered_values, filtered_names = (), ()

        return swizzledtuple(
            typename,
            filtered_names,
            rename=rename,
            defaults=filtered_values,
            module=module,
            arrange_names=arrange_names[index],
            sep=sep,
        )()

    for method in (
        __new__,
        _make.__func__,
        _replace,
        __repr__,
        _asdict,
        __getnewargs__,
        __getattribute__,
        __getitem__,
    ):
        method.__qualname__ = f"{typename}.{method.__name__}"

    class_namespace = {
        "__doc__": f"{typename}({arg_list})",
        "__slots__": (),
        "_fields": field_names,
        "_field_defaults": field_defaults,
        "__new__": __new__,
        "_make": _make,
        "_replace": _replace,
        "__repr__": __repr__,
        "_asdict": _asdict,
        "__getnewargs__": __getnewargs__,
        "__getattribute__": __getattribute__,
        "__getitem__": __getitem__,
    }
    seen = set()
    for index, name in enumerate(arrange_names):
        if name in seen:
            continue
        doc = _sys.intern(f"Alias for field number {index}")
        class_namespace[name] = _tuplegetter(index, doc)
        seen.add(name)

    result = type(typename, (tuple,), class_namespace)

    if module is None:
        try:
            module = _sys._getframemodulename(1) or "__main__"
        except AttributeError:
            try:
                module = _sys._getframe(1).f_globals.get("__name__", "__main__")
            except (AttributeError, ValueError):
                pass
    if module is not None:
        result.__module__ = module

    return result


# Helper function to split a string based on a sep
def split_string(string, sep):
    if sep[0] == "+":
        n = int(sep)
        return [string[i : i + n] for i in range(0, len(string), n)]
    else:
        return string.split(sep)


# Helper function to collect attribute retrieval functions from a class or meta-class
def collect_attribute_functions(cls):
    funcs = []
    if hasattr(cls, "__getattribute__"):
        funcs.append(cls.__getattribute__)
    if hasattr(cls, "__getattr__"):
        funcs.append(cls.__getattr__)
    if not funcs:
        raise AttributeError(
            "No __getattr__ or __getattribute__ found on the class or meta-class"
        )
    return funcs


# Function to combine multiple attribute retrieval functions


def is_valid_sep(s):
    # if not s:
    #     return False
    if s[0] == "+" and s[1:].isdigit():
        return True
    for ch in s:
        if ch == "_":
            continue
        cat = unicodedata.category(ch)
        if not (cat.startswith("L") or cat == "Nd"):
            return False
    return True


def swizzle_attributes_retriever(
    attribute_funcs=None, sep=None, type=swizzledtuple, only_attrs=None
):
    trie = None

    if sep == "":
        sep = "+1"  # for backwards compatibility, remove on next version

    if sep is None and only_attrs:
        only_attrs_length = set(len(fname) for fname in only_attrs)
        if len(only_attrs_length) == 1:
            sep = f"+{next(iter(only_attrs_length))}"
        else:
            trie = Trie(only_attrs)

    if sep is not None and not is_valid_sep(sep):
        raise ValueError(
            f"Invalid value for sep: {sep!r}. Must be either:"
            " (1) a non-empty string containing only letters, digits, or underscores, "
            "or (2) a pattern of the form '+N' where N is a positive integer."
        )

    def _swizzle_attributes_retriever(attribute_funcs):
        if not isinstance(attribute_funcs, list):
            attribute_funcs = [attribute_funcs]

        def retrieve_attribute(obj, attr_name):
            for func in attribute_funcs:
                try:
                    return func(obj, attr_name)
                except AttributeError:
                    continue
            return MISSING

        @wraps(attribute_funcs[-1])
        def retrieve_swizzled_attributes(obj, attr_name):
            # Attempt to find an exact attribute match
            attribute = retrieve_attribute(obj, attr_name)
            if attribute is not MISSING:
                return attribute

            matched_attributes = []
            arranged_names = []
            # If a sep is provided, split the name accordingly
            if sep is not None:
                attr_parts = split_string(attr_name, sep)
                arranged_names = attr_parts
                for part in attr_parts:
                    if only_attrs and part not in only_attrs:
                        raise AttributeError(
                            f"Attribute {part} is not part of an allowed field for swizzling"
                        )
                    attribute = retrieve_attribute(obj, part)
                    if attribute is not MISSING:
                        matched_attributes.append(attribute)
                    else:
                        raise AttributeError(f"No matching attribute found for {part}")
            elif only_attrs:
                arranged_names = trie.split_longest_prefix(attr_name)
                if arranged_names is None:
                    raise AttributeError(f"No matching attribute found for {attr_name}")
                for name in arranged_names:
                    attribute = retrieve_attribute(obj, name)
                    if attribute is not MISSING:
                        matched_attributes.append(attribute)
                    else:
                        raise AttributeError(f"No matching attribute found for {name}")
            else:
                # No sep provided, attempt to match substrings
                i = 0
                while i < len(attr_name):
                    match_found = False
                    for j in range(len(attr_name), i, -1):
                        substring = attr_name[i:j]
                        attribute = retrieve_attribute(obj, substring)
                        if attribute is not MISSING:
                            matched_attributes.append(attribute)
                            arranged_names.append(substring)
                            i = j  # Move index to end of the matched substring
                            match_found = True
                            break
                    if not match_found:
                        raise AttributeError(
                            f"No matching attribute found for substring: {attr_name[i:]}"
                        )

            if type == swizzledtuple:

                seen = set()
                field_names, field_values = zip(
                    *[
                        (name, matched_attributes[i])
                        for i, name in enumerate(arranged_names)
                        if name not in seen and not seen.add(name)
                    ]
                )

                name = "swizzledtuple"
                if hasattr(obj, "__name__"):
                    name = obj.__name__
                elif hasattr(obj, "__class__"):
                    if hasattr(obj.__class__, "__name__"):
                        name = obj.__class__.__name__
                result = type(
                    name,
                    field_names,
                    arrange_names=arranged_names,
                    sep=sep,
                )
                result = result(*field_values)
                return result

            return type(matched_attributes)

        return retrieve_swizzled_attributes

    if attribute_funcs is not None:
        return _swizzle_attributes_retriever(attribute_funcs)
    else:
        return _swizzle_attributes_retriever


def swizzle(cls=None, meta=False, sep=None, type=tuple, only_attrs=None):

    def preserve_metadata(
        target,
        source,
        keys=("__name__", "__qualname__", "__doc__", "__module__", "__annotations__"),
    ):
        for key in keys:
            if hasattr(source, key):
                try:
                    setattr(target, key, getattr(source, key))
                except (TypeError, AttributeError):
                    pass  # some attributes may be read-only

    def class_decorator(cls):
        # Collect attribute retrieval functions from the class
        attribute_funcs = collect_attribute_functions(cls)

        # Apply the swizzling to the class's attribute retrieval
        setattr(
            cls,
            attribute_funcs[-1].__name__,
            swizzle_attributes_retriever(attribute_funcs, sep, type, only_attrs),
        )

        # Handle meta-class swizzling if requested
        if meta:
            meta_cls = _type(cls)

            class SwizzledMetaType(meta_cls):
                pass

            if meta_cls == EnumMeta:

                def cfem_dummy(*args, **kwargs):
                    pass

                cfem = SwizzledMetaType._check_for_existing_members_
                SwizzledMetaType._check_for_existing_members_ = cfem_dummy

            class SwizzledClass(cls, metaclass=SwizzledMetaType):
                pass

            if meta_cls == EnumMeta:
                SwizzledMetaType._check_for_existing_members_ = cfem

            # Preserve metadata on swizzled meta and class
            preserve_metadata(SwizzledMetaType, meta_cls)
            preserve_metadata(SwizzledClass, cls)

            meta_cls = SwizzledMetaType
            cls = SwizzledClass

            meta_funcs = collect_attribute_functions(meta_cls)
            setattr(
                meta_cls,
                meta_funcs[-1].__name__,
                swizzle_attributes_retriever(meta_funcs, sep, type, only_attrs),
            )
        return cls

    if cls is None:
        return class_decorator
    else:
        return class_decorator(cls)


t = swizzledtuple
# c = swizzledclass


class Swizzle(types.ModuleType):
    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        self.__dict__.update(_sys.modules[__name__].__dict__)

    def __call__(
        self, cls=None, meta=False, sep=None, type=swizzledtuple, only_attrs=None
    ):
        return swizzle(cls, meta, sep, type, only_attrs)


_sys.modules[__name__] = Swizzle()
