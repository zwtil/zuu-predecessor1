
def test_fileproperty():
    from zrcl.file import FileProperty

    with open("test.toml", "w") as f:
        f.write("test = 1\n")

    class test:
        x = FileProperty("test.toml")

    assert test.x["test"] == 1

    with open("test.toml", "w") as f:
        f.write("test = 2\n")

    assert test.x["test"] == 2


