import pprint
import time

from zrcl.ext_yaml import FloYaml



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

    dumped = parsed.dumps()
    dumped = dumped.splitlines()

def test_floyaml_2():
    data = """\
task: operation-alpha
  time_start: 13:00
  time_limit: 60min
  action: initiate-alpha
    execute: ${path_generic}/exec_cmd alpha --target ${target_alpha}

  on_completion: cleanup-alpha
    terminate_all: True

task: operation-beta
  time_start: 14:00
  time_limit: 60min
  action: initiate-beta
    execute: ${path_generic}/exec_cmd beta {param_beta}
    wait: 1min

  on_completion: cleanup-beta
    terminate_all: True

task: operation-gamma
  time_start: 15:00
  time_limit: 60min
  action: initiate-gamma
    execute: ${path_generic}/exec_cmd gamma {param_gamma}
      
  on_completion: cleanup-gamma
    terminate_all: True

process: procedure-delta
  boundary: all
  frequency: 5min

procedure: process-epsilon
  trigger: ${path_generic}/exec_cmd epsilon
    run: ${path_generic}/exec_cmd kill --name ${name_epsilon}

procedure: process-zeta
  trigger: ${path_generic}/exec_cmd zeta-launch
    run: ${path_generic}/exec_cmd launch --name ${name_zeta} --package ${pkg_zeta}

    """
    processed = FloYaml(data)

    pprint.pprint(processed.datadict)