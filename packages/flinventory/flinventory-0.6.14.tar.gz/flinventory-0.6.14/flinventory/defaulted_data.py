#! /usr/bin/env python3
"""Data structures for objects with fallback.

This module provides a dict-like data structure, maybe later
also other data structures, that can provide information
from a different default data storage if it does not provide
it itself but is still editable.

To keep the special cases at bay, the supported data types are limited:
- keys: str, tuple(str, language key (which is a str as well))
- values: str, int, float, bool, None, list of the simple ones
- when list is accessed, always tuple is returned
- list-altering functions are supplied
"""

import logging

import collections

from typing import Any, Iterable, Union, Iterator, cast, Callable

from . import constant

IMMUTABLE_TYPES = (str, int, float, bool, type(None))
Immutable = Union[*IMMUTABLE_TYPES]
Key = Union[str, tuple[str, str]]
"""Type of keys of DefaultedDict"""
Value = Union[Immutable, list[Immutable]]
"""Type of values of DefaultedDict"""
Data = collections.abc.Mapping[Key, Value]
"""Type of data that can be used as default and starting data."""
SuperDict = collections.abc.MutableMapping[Key, Value]
"""Super type of DefaultedDict."""


class DefaultedDict(SuperDict):
    """A dict that returns information from a default dict if needed.

    The DefaultedDict is not subclassed from dict or UserDict so that
    we have to think for every functionality how it should be implemented.

    For simplicity only some value types are allowed:
    - immutable values
    - lists of immutable values

    For simplicity only some key types are allowed:
    - str
    - tuple[str, str|int] for translated keys (where ints are converted to language keys)

    """

    def __init__(
        self,
        data: collections.abc.Mapping[Key, Value],
        default: collections.abc.Mapping[Key, Value],
        non_defaulted: Iterable[str],
        translated: Iterable[str],
        lists: Iterable[str],
        default_order: Iterable[str],
        options: constant.Options,
    ):
        """Creates a defaulted dict.

        Args:
            data: data at the beginning. Is converted as if all elements where inserted one by one.
            default: other dict where to draw information from where this dict has none.
                Use empty dict if no default values exist.
            non_defaulted: keys that should not use data from default
            translated: keys that are used as a tuple (this_key, language) for translated values
            lists: keys (and tuples of (this_key, language) of list value
            default_order: default order of keys when iterating or turning into regular dict
        """
        self._logger = logging.getLogger(__name__)
        self._default = default
        self._non_defaulted = tuple(non_defaulted)
        self._translated = tuple(translated)
        self._lists = tuple(lists)
        self._default_order = tuple(default_order)
        self._options = options
        self._data = {}
        for key, value in data.items():
            self[key] = value  # type checking and so on
        if isinstance(data, DefaultedDict):
            logging.getLogger(__name__).debug(
                f"Check that it's correctly saved: {data!r} -> {self!r}."
            )

    @property
    def default(self):
        """The default values."""
        return self._default

    @property
    def non_defaulted(self) -> tuple[str, ...]:
        """Tuple of keys that do not use default."""
        return tuple(self._non_defaulted)

    @property
    def translated(self) -> tuple[str, ...]:
        """Tuple of keys that should be called as a (key, language_key)."""
        return tuple(self._translated)

    @property
    def lists(self) -> tuple[str, ...]:
        """Tuple of keys that hold lists."""
        return tuple(self._lists)

    @property
    def default_order(self) -> tuple[str, ...]:
        """Default order of keys. Not changable."""
        return tuple(self._default_order)

    def best(self, translated_key, **backup):
        """For a translated key, get the 'best' value.

        That is: get the value for the language that is highest in the options.languages list.

        Args:
            translated_key: key for which a value is looked for. Must be in self.translated.
            **backup: if the key-word-only argument 'backup' is given, use this as the default value
                If no such argument is given, raise KeyError
        Raises:
            KeyError: if no arguments are given and no value could be found
        """
        assert translated_key in self.translated
        for language in self._options.languages:
            try:
                return self[translated_key, language]
            except KeyError:
                pass
        for key in self:
            # also searches in default
            if isinstance(key, tuple) and len(key) == 2 and key[0] == translated_key:
                return self[key]
        if "backup" in backup:
            return backup["backup"]
        raise KeyError(f"No {translated_key} in {self!r} known.")

    @staticmethod
    def _key_in_category(key: Key, category: Iterable[str]) -> bool:
        """Is the key in one of the categories (lists, non_defaulted, translated)?

        In case of tuple only regard the first element since the second is a language key.
        """
        return key in category or (isinstance(key, tuple) and key[0] in category)

    def interpret_number_language(self, key: Union[Key, tuple[str, int]]) -> Key:
        """Transform key in case of type (translatable, number). Otherwise return as is."""
        try:
            return (key[0], self._options.languages[key[1]])
            # checks implicitly:
            # and isinstance(key, tuple)
            # and len(key) > 1
            # and isinstance(key[1], int)
        except (IndexError, TypeError):
            return key

    def get_conversion(self, key: Key) -> Callable[[Any], Any]:
        """Choose the correct conversion from saved value to given value based on key.

        Can be tuple for lists or identity for everything else.
        """
        return (
            tuple if DefaultedDict._key_in_category(key, self._lists) else lambda x: x
        )

    def __getitem__(self, key: Union[Key, tuple[str, int]]) -> Value:
        """Give item for ["key"] syntax. Use default is needed.

        Returns:
            in order of preference:
            - internally saved value
            - value in default
            - in case of translated keys: dictionary language_key : value, also including default
              values. Note that changing this dictionary does not change the value of self.
              Does not include translated values for language codes that are not listed
              in options.
        Raises:
            KeyError: if key does not exist and default has not key either
                or key is in self.non_defaulted. Also raises KeyError if a translated key
                is queried and no translations are available (no empty dict is given in this case).
        """
        key = self.interpret_number_language(key)
        conversion = self.get_conversion(key)

        try:
            return conversion(self._data[key])
        except KeyError as key_error:
            if DefaultedDict._key_in_category(key, self._non_defaulted):
                raise KeyError(f"Default not used for {key}") from key_error
            try:
                return conversion(self._default[key])
            except KeyError:
                if key in self._translated:
                    translations = {}
                    for lang_key in self._options.languages:
                        try:
                            translations[lang_key] = conversion(self[(key, lang_key)])
                        except KeyError:
                            # does not exist
                            pass
                    if translations:
                        return translations
                # else:
                raise KeyError(f"{key} has no value.") from key_error

    def get_undefaulted(self, key: Key, **backup: Value) -> Value:
        """Get a value but without resorting to "backup".

        Args:
            key: the key for which the value is looked for.
                Can be (translatable, nr) which is interpreted as in __getitem__.
                Cannot be translatable without language key.
                (If that is necessary in the same way as for [key], it needs to be implemented.)
            backup: optional keyword-only argument "backup". Used if no value is saved.
                If not given, KeyError is raised.
        Returns:
            internalData.get(key, backup) or internalData[key]
        """
        key = self.interpret_number_language(key)
        conversion = self.get_conversion(key)
        try:
            return conversion(self._data[key])
        except KeyError:
            if "backup" in backup:
                return backup["backup"]
            raise

    def __setitem__(
        self, key: Union[Key, tuple[str, int]], value: Union[Value, dict[str, Value]]
    ) -> None:
        """Sets a value.

        Checks the type: if it should be a list, then check that it is.
        Otherwise, check that it is Immutable.

        If language is needed but not given,
            use first language in options if a list or single value is given,
            set all languages if dict is given.
        If language is given as an integer, use the language at this index.
        Args:
            key: new key
            value: new value. If key in self.translated, must be dict.
        Raises:
            AssertionError: in case of wrong types. This is chosen to give
                a confident caller the possibility to optimize this away.
            TypeError: if value should be a list but is not iterable
            Value Error: if value is not a dict for key in translated.
                Setting individual values is probably preferable.
        """
        if isinstance(key, str) and any(
            key.endswith("_" + (found_language := language))
            for language in self._options.languages
        ):
            main_key = key[: -len("_" + found_language)]
            if main_key in self._translated:
                new_key = (main_key, found_language)
                key = new_key
            else:
                self._logger.warning(
                    f"debug: found {key} ({found_language}) but {main_key} "
                    "should not be translated"
                )
        ### up until here could be deleted when data is converted

        if key in self._translated:
            assert isinstance(key, str)
            # must be str, not (str, language) since _translated has only str
            # therefore the following recursive calls do not create an infinite
            # recursion
            if isinstance(value, dict):
                for language, subvalue in value.items():
                    self[key, language] = subvalue
            else:
                self[key, self._options.languages[0]] = value
            return  # otherwise the original key would be used below

        if DefaultedDict._key_in_category(key, self._lists) and isinstance(
            value, IMMUTABLE_TYPES
        ):
            value = [value]

        ##### Datatype assertions
        if DefaultedDict._key_in_category(key, self._lists):
            # str is iterable, so to forbid it, it needs to be handled differently
            assert not isinstance(
                value, str
            ), f"Key {key} is only storing lists, not strings like {value}."
            try:
                value = list(value)
            except TypeError:
                assert (
                    False
                ), f"Key {key} is only taking storing lists, so supply some iterable, not {value}."
            assert all(
                isinstance(mutable := element, IMMUTABLE_TYPES) for element in value
            ), f"{mutable} of type {type(mutable)} is not allowed in list in our dicts."
        else:
            assert isinstance(
                value, IMMUTABLE_TYPES
            ), f"Values for key {key} must be immutable, not {type(value)} as {value} is."
        ###### Datatype assertions end

        if DefaultedDict._key_in_category(key, self._translated):
            # cannot be simple str since we checked that at beginning
            assert isinstance(
                key, tuple
            ), "If a translatable key is given, it must be a tuple of length 2."
            assert (
                len(key) == 2
            ), "If a translatable key is given, it must be a tuple of length 2."
            try:
                key = key[0], self._options.languages[cast(int, key[1])]
            except TypeError:  # probably key[1] is str, not int.
                pass  # it's fine
            except IndexError:
                assert False, f"There are not {cast(int, key[1]) + 1} many languages."
            assert isinstance(key[1], str), "Second part of key must be integer or str"
        else:
            assert isinstance(key, str), f"Key {key} has to be a string but."
        self._data[key] = value

    def to_jsonable_data(self) -> dict[str, Any]:
        """Returns values without resorting to default.

        Intended to be used for saving to file.

        Returns:
            dict with
            key: value for non-translated keys
            key: { lang: value } for translated keys
        """
        # make sure that all keys in saveable will be strings:
        assert all(
            ((non_str := key) not in self._translated and isinstance(key, str))
            or (
                isinstance(key, tuple)
                and len(key) == 2
                and isinstance(key[0], str)
                and isinstance(key[1], str)
                and key[0] in self._translated
            )
            for key in self._data
        ), f"{non_str} is an invalid key. Only strings (and tuple for translated keys) allowed."

        saveable = {}
        for key, value in self._data.items():
            if isinstance(key, tuple):
                assert (
                    len(key) == 2
                ), f"Somehow a weird tuple key was introduced: {key}."
                if key[0] in saveable:
                    saveable[key[0]][key[1]] = value
                else:
                    saveable[key[0]] = {key[1]: value}
            else:
                saveable[key] = value
        assert all(
            isinstance(saveable[mutable := key], IMMUTABLE_TYPES)
            or key in self._lists
            or key in self._translated
            for key in saveable
        ), (
            f"Value {saveable[mutable]} of type {type(saveable[mutable])}"
            f" for key {mutable} is mutable but should not be."
        )
        assert all(
            key not in self._lists
            or key in self._translated
            or (
                isinstance(saveable[not_list := key], list)
                and all(isinstance(element, IMMUTABLE_TYPES) for element in value)
            )
            for key, value in saveable.items()
        ), (
            f"Value {saveable[not_list]} for key {not_list} "
            "is not a list or some element is mutable."
        )
        assert all(
            (wrong := key) in self._lists
            or key not in self._translated
            or (
                isinstance(value, dict)
                and all(isinstance(value[subkey], IMMUTABLE_TYPES) for subkey in value)
            )
            for key, value in saveable.items()
        ), (
            f"Value {saveable[wrong]} for key {wrong} is somehow wrong. "
            "Should be dict of immutable values."
        )
        assert all(
            (wrong := key) not in self._lists
            or key not in self._translated
            or (
                isinstance(value, dict)
                and all(
                    isinstance(value[subkey], list)
                    and all(
                        isinstance(value, IMMUTABLE_TYPES) for value in value[subkey]
                    )
                    for subkey in value
                )
            )
            for key, value in saveable.items()
        ), (
            f"Value {saveable[wrong]} for key {wrong} is somehow wrong. "
            "Should be dict of lists of immutable values."
        )

        assert all(
            isinstance(wrong_key := element, str)
            and (
                isinstance(wrong_type := value, IMMUTABLE_TYPES)
                or (
                    isinstance(value, list)
                    and all(isinstance(subvalue, IMMUTABLE_TYPES) for subvalue in value)
                )
                or (
                    isinstance(value, dict)
                    and all(
                        isinstance(subkey, str)
                        and (
                            isinstance(sub_value, IMMUTABLE_TYPES)
                            or (
                                isinstance(sub_value, list)
                                and all(
                                    isinstance(sub_sub_value, IMMUTABLE_TYPES)
                                    for sub_sub_value in sub_value
                                )
                            )
                        )
                        for subkey, sub_value in value.items()
                    )
                )
            )
            for element, value in saveable.items()
        ), f"{wrong_key} = {wrong_type} occurs in json output. Not allowed."

        # todo: ensure order of self._default_order
        return saveable

    def __delitem__(self, key: Key):
        """Removes an item.

        Allows removing all translated values.

        Note that [key] might still return something since default values are not deleted.
        Note that (str, int)-type keys as in getitem and setitem are not supported.

        Raises:
            KeyError: if key is not valid.
        """
        assert (
            not isinstance(key, tuple) or len(key) == 2 and isinstance(key[1], str)
        ), f"(str, int) as {key} keys are not supported by del yet."
        if key in self._translated:
            del_something = False
            for other_key in set(
                k for k in self._data if isinstance(k, tuple) and k[0] == key
            ):
                # set() copies keys. If we directly iterate
                # over self._data, we get RuntimeError: dictionary changed size during iteration
                del self._data[other_key]
                del_something = True
            if not del_something:
                raise KeyError(key)
        else:
            del self._data[key]

    def items(self) -> Iterable[tuple[Key, Value]]:
        """Iterate over all directly saved key-value pairs.

        Do not include values only saved in the default.
        """
        # custom __getitem__ is not used but that's fine because we
        # do not want default values
        # and also giving the original lists is fine since they are
        # not from the default and therefore fine to edit
        return self._data.items()

    def all_items(self):
        """Iterator over all key-value pairs saved in self and default.

        No performance improvement over iterating over self and using [key].
        """
        for key in iter(self):
            yield key, self[key]

    def get(self, key, default=None):
        """Get value without KeyError, instead with default.

        Returns:
            value saved for key itself if it exists
            otherwise value saved in objects default for key if it exists
            otherwise argument default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: Key):
        """Return if self[key] would give something, possibly from default."""
        try:
            _ = self[key]
        except KeyError:
            return False
        return True

    def __iter__(self) -> Iterator[Key]:
        """Iterate over keys with values in self and defaults.

        Each translation of a translated key is given separately.
        """
        already_sent = set()
        for key in self._data:
            already_sent.add(key)
            yield key
        for key in self.default:
            if key not in already_sent and not self._key_in_category(
                key, self._non_defaulted
            ):
                already_sent.add(key)  # should not be necessary, but to make sure
                yield key
            # else: go to next

    def __keys__(self) -> set[Key]:
        """iter(self) as a set."""
        return set(iter(self))

    def __str__(self):
        """Give string representation of data directly saved. (Without default values)"""
        return f"{self._data}"

    def __repr__(self):
        """Give string representation of data including special keys and defaults."""
        return f"""DefaultedDict(
    data={self._data!r},
    lists={self.lists!r},
    translated={self.translated!r},
    non_defaulted={self.non_defaulted!r},
    default={repr(self.default).replace('\n', '\n    ')},
    languages={self._options.languages!r}
    """

    def __len__(self):
        """Give amount of keys with values directly in self.

        Ignore keys available in default.
        Translated keys are counted as often as they have translations.
        """
        return len(self._data)
