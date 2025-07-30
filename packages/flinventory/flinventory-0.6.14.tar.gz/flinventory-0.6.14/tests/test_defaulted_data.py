#!/usr/bin/env python
"""Tests for defaulted data.

This should be turned into a proper test suite with pytest or something else.

But until then it is just a bunch of functions that test some (edge)cases
for usage of defaultedData.
"""
from ..flinventory import constant
from ..flinventory import DefaultedDict


def test_creation_empty():
    empty = DefaultedDict({}, {}, [], [], [], [], constant.Options({}))
    try:
        print(empty["someKey"])
    except KeyError:
        pass
    else:
        assert False, "empty Defaulted dict ['someKey'] should raise KeyError"
    empty["someKey"] = "Some immutable value"
    assert empty["someKey"] == "Some immutable value"
    empty.default["someOther"] = "Something else"
    assert empty["someOther"] == "Something else"
    try:
        empty["listKey"] = [1, 2, 3]
    except AssertionError:
        pass
    else:
        assert False, "only list keys should accept lists"


def test_with_dict_default():
    backup = {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3]}
    dd = DefaultedDict(
        {"bla": "hi", ("name", "en"): "Lib", "l": [5]},
        default=backup,
        non_defaulted=["krukz"],
        translated=["name"],
        lists=["l"],
        default_order=[],
        options=constant.Options({}),
    )
    assert dd["bla"] == "hi"
    assert dd["name"] == {"de": "Bibo", "en": "Lib"}
    assert list(dd["l"]) == [5]
    assert dd["hi"] == "du"
    backup["krukz"] = "toll"
    try:
        print(dd["krukz"])
    except KeyError:
        pass  # because non_defaulted
    else:
        assert False, "krukz not defined"
    dd["krukz"] = "murkz"
    assert dd["krukz"] == "murkz"
    dd["name"]["de"] == "was anderes"  # wird ignoriert
    assert dd[("name", "de")] == "Bibo"
    export = dd.to_jsonable_data()
    assert export == {"bla": "hi", "name": {"en": "Lib"}, "l": [5], "krukz": "murkz"}


def test_setting_multiple_languages():
    dd = DefaultedDict(
        {},
        default={},
        non_defaulted=[],
        translated=["name"],
        lists=[],
        default_order=[],
        options=constant.Options({}),
    )
    dd["name"] = {0: "Schraubkranz", "en": "freewheel"}
    assert dd.to_jsonable_data() == {"name": {"de": "Schraubkranz", "en": "freewheel"}}


def test_init_type_check_list():
    backup = {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3]}
    try:
        dd = DefaultedDict(
            {"bla": "hi", ("name", "en"): "Lib", "l": 5},
            default=backup,
            non_defaulted=["krukz"],
            translated=["name"],
            lists=["l"],
            default_order=[],
            options=constant.Options({}),
        )
    except AssertionError:
        pass
    else:
        assert False, "DefaultedDict with list key accepts number"


def test_init_type_check_list2():
    backup = {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3]}
    try:
        dd = DefaultedDict(
            {"bla": "hi", ("name", "en"): "Lib", "l": "someIterableString"},
            default=backup,
            non_defaulted=["krukz"],
            translated=["name"],
            lists=["l"],
            default_order=[],
            options=constant.Options({}),
        )
    except TypeError:
        pass
    else:
        assert False, "DefaultedDict with list key accepts str"


def test_init_type_check_list2():
    params = {
        "translated": ["name"],
        "lists": ["l", "ll"],
        "default_order": [],
        "options": constant.Options({}),
    }
    backup = DefaultedDict(
        {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3]},
        default={},
        non_defaulted=[],
        **params,
    )
    dd = DefaultedDict(
        {"bla": "hi", ("name", "en"): "Lib", "l": [3, 4, 5]},
        default=backup,
        non_defaulted=["krukz"],
        **params,
    )
    dd2 = DefaultedDict(dd, default=backup, non_defaulted=["krukz"], **params)
    assert dd == dd2
    assert dd["bla"] == "hi"
    assert (
        dd["name", "en"] == "Lib"
    )  # note the missing () because the comma makes the tuple, not the ()
    assert dd["name", "de"] == "Bibo"
    try:
        dd["l"].append(6)
    except AttributeError:
        pass
    else:
        assert False, "list should be converted to tuple, no append exist"
    dd2["l"] == [3, 4, 5]
    dd2.default["l"] == [1, 2, 3]
    backup["ll"] = another = list("another")
    assert list(dd["ll"]) == another
    assert list(dd["ll"]) == another
    del backup["ll"]
    try:
        print(dd["ll"])
        print(dd2["ll"])
    except KeyError:
        pass
    else:
        assert (
            False
        ), "after deleting value in default, should not be accessible anymore"
    dd["ll"] = another
    try:
        print(dd2["ll"])
    except KeyError:
        pass
    else:
        assert False, "dd and dd2 should be independant"
    try:
        dd2["ll"] = "Hallo"
    except AssertionError:
        pass
    else:
        assert (
            False
        ), "assigning a string to a list-valued key should result in TypeError"
    try:
        dd2["something Weird"] = [9, "hi", "lb"]
    except AssertionError:
        pass
    else:
        assert (
            False
        ), "assigning list to a non-list-valued key should result in TypeError"
    dd["name"] = "toller Name"
    assert dd["name", "de"] == "toller Name"


def test_get_with_default():
    params = {
        "translated": ["name"],
        "lists": ["l", "ll"],
        "default_order": [],
        "options": constant.Options({}),
    }
    backup = DefaultedDict(
        {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3]},
        default={},
        non_defaulted=[],
        **params,
    )
    dd = DefaultedDict(
        {"bla": "hi", ("name", "en"): "Lib", "l": [3, 4, 5]},
        default=backup,
        non_defaulted=["krukz"],
        **params,
    )
    assert (
        result := dd.get("bla", "otherDefault")
    ) == "hi", f"Get does not work with existing data: dd.get('bla', 'otherDefault') = {result}"
    assert (
        result := dd.get("hi", "otherDefault")
    ) == "du", f"Get does not with standard default data: dd.get('hi', 'otherDefault') = {result}"
    assert (
        result := dd.get("otherKey", "otherDefault")
    ) == f"otherDefault", f"Get does not use fallback default: dd.get('otherKey', 'otherDefault') = {result}"


def test_ignore_default_for_contain_check():
    params = {
        "translated": ["name"],
        "lists": ["l", "ll"],
        "default_order": [],
        "options": constant.Options({}),
    }
    backup = DefaultedDict(
        {"hi": "du", "bla": "blub", ("name", "de"): "Bibo", "l": [1, 2, 3], "krukz": 4},
        default={},
        non_defaulted=[],
        **params,
    )
    dd = DefaultedDict(
        {"bla": "hi", ("name", "en"): "Lib", "l": [3, 4, 5]},
        default=backup,
        non_defaulted=["krukz"],
        **params,
    )
    assert "bla" in dd
    assert "l" in dd
    assert "x" not in dd
    assert "hi" in dd
    assert "hi" not in dd._data
    del dd["bla"]
    assert "bla" in dd
    assert "bla" not in dd._data
    assert dd["bla"] == "blub"
    assert "krukz" not in dd
    try:
        print(f"krukz = {dd['krukz']}")
    except KeyError:
        pass
    else:
        assert False, "krukz should not be used from default"
    try:
        del dd["krukz"]
    except KeyError:
        pass
    else:
        assert False, "krukz does not exist directly, should not be deletable"
    del dd["name"]
    assert dd["name", "de"] == "Bibo"
    assert ("name", "de") in dd
    assert ("name", "en") not in dd
    assert dd["name"] == {"de": "Bibo"}
    try:
        should_not_exist = dd["name", "en"]
    except KeyError:
        pass
    else:
        assert False, (
            f'("name", "en") should not be {should_not_exist} '
            f"but raise KeyError after deletion"
        )


if __name__ == "__main__":
    test_creation_empty()
    test_with_dict_default()
    test_init_type_check_list()
    test_init_type_check_list2()
    test_get_with_default()
    test_ignore_default_for_contain_check()
    test_setting_multiple_languages()
