"""
test_validator.py — Five tests for name_validator.py.

Run with: python -m pytest tests/test_validator.py -v
(Use python -m pytest, not plain pytest, so Python finds the modules/ folder.)
"""

from modules.name_validator import validate_names


def test_catches_fake_filename():
    """A fake backticked filename must appear in invalid."""
    tree = ["src/app.py", "src/utils.py", "README.md"]
    narration = "You enter `src/app.py` and see `src/fake.py`."
    result = validate_names(narration, tree)
    assert result["invalid"] == ["src/fake.py"]


def test_passes_real_filename():
    """Real backticked filenames must not appear in invalid."""
    tree = ["src/app.py", "README.md"]
    narration = "You enter `src/app.py` and find the `README.md`."
    result = validate_names(narration, tree)
    assert result["invalid"] == []


def test_accepts_real_dependency_name():
    """A dependency name in backticks must not be flagged."""
    tree = ["src/app.py"]
    narration = "A key named `requests` glints on the floor."
    result = validate_names(narration, tree, dependencies=["requests"])
    assert result["invalid"] == []


def test_prose_slashes_are_not_flagged():
    """Slash-paths whose first segment is not real must not be checked."""
    tree = ["src/app.py"]
    narration = "Use and/or magic in input/output land."
    assert validate_names(narration, tree)["invalid"] == []


def test_trailing_period_is_not_flagged():
    """A real filename with trailing punctuation must not be flagged."""
    tree = ["src/app.py"]
    narration = "The path is src/app.py."
    assert validate_names(narration, tree)["invalid"] == []
