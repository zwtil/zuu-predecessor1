


from zrcl.ext import FrozenDict


def test_dictkeysdict_1():
    from zrcl.ext import DictKeysDict

    d = DictKeysDict(
        {"string": "Hello, world!", "int": 42, "list": [1, 2, 3], "dict": {"a": 1, "b": 2},
        "{\"what\" : 24}" : { "{\"what\" : 24, \"why\" : 42}" : "Hello, world!", "int": 42, "list": [1, 2, 3], "dict": {"a": 1, "b": 2},} ,
        "www" :  {
            "www" : {FrozenDict({"k" : 23}) : 24}}
        }
    )

    assert d[FrozenDict({"what" : 24})] == DictKeysDict({"{\"what\" : 24, \"why\" : 42}": "Hello, world!", "int": 42, "list": [1, 2, 3], "dict": {"a": 1, "b": 2},})
    assert d["www"]["www"] == DictKeysDict({FrozenDict({"k" : 23}) : 24}) 
    w = DictKeysDict.dumpJson(d)
    l = DictKeysDict.loadJson(w)
    print(d)
    print(l)
    assert d == l