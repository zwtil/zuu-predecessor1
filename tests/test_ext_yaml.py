import time

def test_floyaml_1():
    from zrcl.ext_yaml import FloYaml

    data = """
    val1: 1
    val2: 2
        val3: 3
        val3: 4
            val5: 5
        val3 : 6
            val5: 10
            val5: 11
        val5: 7
    
    """
    starttime = time.time()
    parsed = FloYaml.load(data)

    print(time.time() - starttime)
    # checks that the parsed data is an instance of the  FloYaml class.
    assert isinstance(parsed, FloYaml)
    """
    checks that the parsed data can be retrieved using
    the FloYaml.VAL method to retrieve all values under the 'val3' key.
    """
    assert parsed["val2", FloYaml.VAL("val3")] == [3,4,6]

    """
    checks that the parsed data can be retrieved using
    the FloYaml.VAL method to retrieve the first value under the 'val3' key.
    """
    assert parsed["val2", FloYaml.VAL("val3[0]")] == 3


    """
    checks that the parsed data can be manipulated using
    the FloYaml class's `__setitem__` method to update the first value under
    the 'val3' key.
    """
    parsed["val2", FloYaml.VAL("val3[0]")] = 4
    assert parsed["val2", FloYaml.VAL("val3[0]")] == 4

    """
    checks that the parsed data can be retrieved again
    using the FloYaml.VAL method to retrieve all values under the 'val3' key
    and verifies that the updated value is present
    """
    assert parsed["val2", FloYaml.VAL("val3")] == [4,4,6]

    """
    checks that the parsed data can be retrieved using the
    FloYaml.VAL method to retrieve all values under the 'val5' key nested
    under the third 'val3' key.
    """
    assert parsed["val2", "val3[2]", FloYaml.VAL("val5")] == [10,11]

    """
    checks that the parsed data can be retrieved using
    the FloYaml class's `__getitem__` method to retrieve the second value
    under the 'val5' key nested under the third 'val3' key
    """
    assert parsed["val2", "val3[2]", "val5[1]"] == 11

    """
    checks that the parsed data can be retrieved using
    the FloYaml class's `__getitem__` method to retrieve a dictionary
    containing the second value under the 'val3' key and all values under
    the 'val5' key nested under the second 'val3' key
    """
    assert parsed["val2", "val3[1]"] == {"__val__": 4, "val5": 5}

    dumped = FloYaml.dumps(parsed)
    dumped = dumped.splitlines()
    pass