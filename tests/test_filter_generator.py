import pytest
from app.filter_generator import generate_custom_blocks, assemble_filter

def test_generate_custom_blocks():
    extracted = {
        'bases': {'Amethyst Ring', 'Leather Belt'},
        'socket_groups': {'BBBB', 'RRR'}
    }
    rules = generate_custom_blocks(extracted)
    
    assert "BaseType \"Amethyst Ring\" \"Leather Belt\"" in rules
    assert "SetBorderColor 0 255 0 255" in rules
    assert "SocketGroup BBBB" in rules
    assert "LinkedSockets >= 4" in rules
    # RRR shouldn't generate a block because len < 4
    assert "SocketGroup RRR\n" not in rules

def test_assemble_filter_with_mock_base():
    extracted = {'bases': {'Amethyst Ring'}}
    mock_base = "# BASE FILTER"
    
    final_filter = assemble_filter(extracted, base_filter_text=mock_base)
    assert "BaseType \"Amethyst Ring\"" in final_filter
    assert "\n# BASE FILTER" in final_filter
