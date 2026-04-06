from app.linter import validate_filter_syntax

def test_valid_syntax():
    text = """
    # This is a comment
    Show
        BaseType "Amethyst Ring"
        SetBorderColor 0 255 0 255
    """
    errors = validate_filter_syntax(text)
    assert len(errors) == 0

def test_invalid_outside_block():
    text = """
    BaseType "Amethyst Ring"
    Show
        SetBorderColor 0 255 0 255
    """
    errors = validate_filter_syntax(text)
    assert len(errors) == 1
    assert "not inside a Show/Hide/Minimal block" in errors[0]

def test_unknown_command():
    text = """
    Show
        MakeItemShiny True
    """
    errors = validate_filter_syntax(text)
    assert len(errors) == 1
    assert "Unknown command" in errors[0]
