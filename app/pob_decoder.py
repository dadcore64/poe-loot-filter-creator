import base64
import zlib
import xml.etree.ElementTree as ET
import urllib.request
import re

def decode_pob_string(pob_input):
    """
    Decodes a PoB input. 
    If it's a pobb.in URL, it fetches the raw data first.
    If it's a base64 string, it decodes and decompresses it.
    """
    pob_input = pob_input.strip()
    
    # Handle pobb.in URLs
    if 'pobb.in' in pob_input:
        # Extract ID and ensure it uses /raw
        pobb_id_match = re.search(r'pobb\.in/([^/\s\?]+)', pob_input)
        if not pobb_id_match:
            raise ValueError("Invalid pobb.in URL format")
        
        pobb_id = pobb_id_match.group(1)
        raw_url = f"https://pobb.in/{pobb_id}/raw"
        
        try:
            req = urllib.request.Request(raw_url, headers={'User-Agent': 'poe-loot-filter-creator'})
            with urllib.request.urlopen(req) as response:
                pob_input = response.read().decode('utf-8').strip()
        except Exception as e:
            raise ValueError(f"Failed to fetch data from pobb.in: {e}")

    # Handle URL-safe base64 characters
    pob_string = pob_input.replace('-', '+').replace('_', '/')
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
            if len(lines) >= 3 and lines[0].startswith('Rarity: '):
                rarity = lines[0].split(': ')[1].strip()
                if rarity in ['RARE', 'UNIQUE']:
                    base_type = lines[2]
                    if not base_type.startswith('{') and "Jewel" not in base_type:
                        extracted_data['bases'].add(base_type)
                        
            # Extract Sockets
            for line in lines:
                if line.startswith('Sockets: '):
                    socks = line.split(': ')[1].strip()
                    groups = socks.split(' ')
                    for g in groups:
                        if len(g) >= 5: # 3-link or more
                            extracted_data['socket_groups'].add(g.replace('-', ''))
                            
    return extracted_data
