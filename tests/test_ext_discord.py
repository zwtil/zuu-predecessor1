from zrcl.ext_discord import EmbedDict, EmbedFactory

def test_embedfactory():
    ed = EmbedDict(
        title="Title",
        description="Description",
        footer={"text": "{k} {k}"},
        fields=[
            {"name": "Field {w}", "value": "Value 1"},
            {"name": "Field 2", "value": "Value 2", "inline": True},
        ],
    )
    e = EmbedFactory.create(
        embed=ed,
        vars={"w": 1, "k" : "www"},
        cache_var="description"
    )

    assert e.footer.text == "www www"

    vars = EmbedFactory.recall_vars(e)
    assert vars == {"w": 1, "k" : "www"}

    assert EmbedFactory.recall_type(EmbedFactory.compute_hash(ed)) == "description"

    vars2 = EmbedFactory.recall_vars(EmbedFactory.compute_hash(e))

    assert vars == vars2

