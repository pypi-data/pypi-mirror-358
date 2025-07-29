import code_tags.__about__
import code_tags.logging_config


def test_imports():
    assert dir(code_tags.__about__)
    assert dir(code_tags.logging_config)
