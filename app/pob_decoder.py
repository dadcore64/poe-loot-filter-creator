import base64
import zlib
import xml.etree.ElementTree as ET

def decode_pob_string(pob_string):
    """Decodes a base64 encoded and zlib compressed PoB string."""
    pob_string = pob_string.replace('-', '+').replace('_', '/')
    padding = len(pob_string) % 4
    if padding:
        pob_string += '=' * (4 - padding)
        
    try:
        decoded_data = base64.b64decode(pob_string)
        xml_data = zlib.decompress(decoded_data)
        return xml_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Invalid PoB string: {e}")

def parse_pob_xml(xml_string):
    """Parses PoB XML to extract relevant data for loot filters."""
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}")
        
    extracted_data = {
        'bases': set(),
        'socket_groups': set()
    }
    
    # Extract from Items
    items_elem = root.find('Items')
    if items_elem is not None:
        for item in items_elem.findall('Item'):
            if not item.text:
                continue
                
            lines = [line.strip() for line in item.text.strip().split('\n')]
            
            # Very rudimentary base item extraction for RARE/UNIQUE
            # Typically: Line 0 = Rarity, Line 1 = Name, Line 2 = Base Type
            if len(lines) >= 3 and lines[0].startswith('Rarity: '):
                rarity = lines[0].split(': ')[1].strip()
                if rarity in ['RARE', 'UNIQUE']:
                    base_type = lines[2]
                    # Filter out generic things or add them
                    if not base_type.startswith('{') and "Jewel" not in base_type:
                        extracted_data['bases'].add(base_type)
                        
            # Extract Sockets (e.g. "Sockets: G-B-R")
            for line in lines:
                if line.startswith('Sockets: '):
                    socks = line.split(': ')[1].strip()
                    # Just an example of grabbing groups
                    groups = socks.split(' ')
                    for g in groups:
                        if len(g) >= 5: # 3-link or more (R-G-B is 5 chars)
                            extracted_data['socket_groups'].add(g.replace('-', ''))
                            
    return extracted_data
