from flask import Blueprint, render_template, request, jsonify, Response
from app.pob_decoder import decode_pob_string, parse_pob_xml
from app.filter_generator import generate_custom_blocks, fetch_neversink_latest, get_filter_backup
from app.linter import validate_filter_syntax
import uuid
import datetime
from app.fallback_filter import FALLBACK_FILTER

main_bp = Blueprint('main', __name__)

# In-memory store for base filters
CACHE = {'neversink': None, 'is_backup': False}

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

@main_bp.route('/api/check_neversink', methods=['GET'])
def check_neversink():
    """Checks if we can fetch the latest filter. If not, returns backup metadata."""
    if CACHE['neversink'] is not None:
        return jsonify({'available': True, 'is_backup': CACHE['is_backup']})

    try:
        CACHE['neversink'] = fetch_neversink_latest()
        CACHE['is_backup'] = False
        return jsonify({'available': True, 'is_backup': False})
    except Exception as e:
        print(f"FETCH FAILED: {e}")
        content, timestamp = get_filter_backup()
        if content:
            dt = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({
                'available': False,
                'has_backup': True,
                'backup_time': dt
            })
        return jsonify({'available': False, 'has_backup': False})

@main_bp.route('/api/use_backup', methods=['POST'])
def use_backup():
    """Explicitly tells the app to use the local backup filter."""
    content, timestamp = get_filter_backup()
    if content:
        CACHE['neversink'] = content
        CACHE['is_backup'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No backup found.'}), 404

@main_bp.route('/api/download', methods=['POST'])
def download_filter():
    data = request.form if request.form else request.json
    if not data:
        return "No data received.", 400

    rules_text = data.get('rules_text', '')
    filter_name = data.get('filter_name', 'custom_build').strip()
    if not filter_name.endswith('.filter'):
        filter_name += '.filter'
        
    errors = validate_filter_syntax(rules_text)
    if errors:
        return f"Invalid syntax in custom rules: {', '.join(errors)}", 400
        
    if CACHE['neversink'] is None:
        try:
            CACHE['neversink'] = fetch_neversink_latest()
            CACHE['is_backup'] = False
        except Exception:
            content, ts = get_filter_backup()
            if content:
                CACHE['neversink'] = content
                CACHE['is_backup'] = True
            else:
                CACHE['neversink'] = FALLBACK_FILTER
                CACHE['is_backup'] = True
        
    final_filter = rules_text + "\n" + CACHE['neversink']
    
    return Response(
        final_filter,
        mimetype="text/plain",
        headers={
            "Content-disposition": f"attachment; filename={filter_name}",
        }
    )
