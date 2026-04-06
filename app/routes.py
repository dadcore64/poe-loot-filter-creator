from flask import Blueprint, render_template, request, jsonify, Response
from app.pob_decoder import decode_pob_string, parse_pob_xml
from app.filter_generator import generate_custom_blocks, fetch_neversink_latest
from app.linter import validate_filter_syntax
import uuid

from app.fallback_filter import FALLBACK_FILTER

main_bp = Blueprint('main', __name__)

# In-memory store for base filters so we don't spam the GitHub API
# In production, use Redis or a file cache with a TTL
CACHE = {'neversink': None}

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/generate_rules', methods=['POST'])
def generate_rules():
    data = request.json
    pob_code = data.get('pob_code', '')
    
    if not pob_code:
        return jsonify({'error': 'PoB code is required.'}), 400
        
    try:
        xml_string = decode_pob_string(pob_code)
        extracted_data = parse_pob_xml(xml_string)
        custom_rules = generate_custom_blocks(extracted_data)
        
        return jsonify({'custom_rules': custom_rules})
    except Exception as e:
        import traceback
        print(f"POB PARSE ERROR: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/validate', methods=['POST'])
def validate_rules():
    data = request.json
    rules_text = data.get('rules_text', '')
    
    errors = validate_filter_syntax(rules_text)
    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors
    })

@main_bp.route('/api/download', methods=['POST'])
def download_filter():
    # Use request.form for normal form submission
    data = request.form if request.form else request.json
    if not data:
        return "No data received.", 400

    rules_text = data.get('rules_text', '')
    filter_name = data.get('filter_name', 'custom_build').strip()
    if not filter_name.endswith('.filter'):
        filter_name += '.filter'
        
    # Validate one last time before combining
    errors = validate_filter_syntax(rules_text)
    if errors:
        return f"Invalid syntax in custom rules: {', '.join(errors)}", 400
        
    # Fetch base filter
    if CACHE['neversink'] is None:
        try:
            print("Attempting to fetch latest NeverSink filter from GitHub...")
            CACHE['neversink'] = fetch_neversink_latest()
        except Exception as e:
            import traceback
            print(f"CRITICAL FETCH ERROR: {traceback.format_exc()}")
            # DO NOT return yet, let it check if None below
            
    # Fallback if fetch failed or returned None
    base_text = CACHE['neversink']
    if base_text is None:
        print("GitHub fetch failed. Using local FALLBACK_FILTER.")
        base_text = FALLBACK_FILTER
        
    final_filter = rules_text + "\n" + base_text
    
    return Response(
        final_filter,
        mimetype="text/plain",
        headers={
            "Content-disposition": f"attachment; filename={filter_name}",
        }
    )
