import pytest

from litsandbox.code_inspect import (
    UnsupportedCodeError,
    validate_python_code,
    func_to_source,
    get_imports,
)


def test_validate_python_code():
    with pytest.raises(ValueError, match="Code cannot be empty or only whitespace"):
        validate_python_code("")

    with pytest.raises(SyntaxError, match="Invalid Python syntax"):
        validate_python_code("for i in range(10): print(i) if i == 5: print('five')")


def fn():
    import lightning_sdk

    print(lightning_sdk.__version__)


def test_func_to_code():
    source = func_to_source(fn)
    assert (
        source
        == """def fn():
    import lightning_sdk

    print(lightning_sdk.__version__)
"""
    )


def test_func_to_code_local():
    def local_fn():
        return

    with pytest.raises(UnsupportedCodeError):
        func_to_source(local_fn)


def test_get_imports():
    source = func_to_source(fn)
    assert get_imports(source) == ["lightning_sdk"]
