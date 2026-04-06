import pytest
import base64
import zlib
from app.pob_decoder import decode_pob_string, parse_pob_xml

def test_decode_valid_pob_string():
    mock_xml = b"<PathOfBuilding><Items></Items></PathOfBuilding>"
    compressed = zlib.compress(mock_xml)
    pob_string = base64.urlsafe_b64encode(compressed).decode('utf-8')
    
    decoded = decode_pob_string(pob_string)
    assert decoded == mock_xml.decode('utf-8')

def test_parse_valid_xml():
    mock_xml = """
    <PathOfBuilding>
        <Items>
            <Item>
Rarity: RARE
Doom Whorl
Amethyst Ring
Sockets: B-B-B
Item Level: 85
            </Item>
        </Items>
    </PathOfBuilding>
    """
    result = parse_pob_xml(mock_xml)
    assert "Amethyst Ring" in result['bases']
    assert "BBB" in result['socket_groups']
