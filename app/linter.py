import re

def validate_filter_syntax(filter_text):
    """
    Very lightweight linter for PoE Filter syntax.
    Returns a list of error strings. Empty list means valid.
    """
    errors = []
    lines = filter_text.split('\n')
    
    valid_blocks = ['Show', 'Hide', 'Minimal']
    in_block = False
    
    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()
        
        # Ignore empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Check if line is a block starter
        if any(line.startswith(vb) for vb in valid_blocks):
            in_block = True
            continue
            
        # If it's not a block starter, it must be inside a block
        if not in_block:
            errors.append(f"Line {i+1}: Statement '{line}' is not inside a Show/Hide/Minimal block.")
            continue
            
        # Validate some common commands (very basic validation)
        # Commands usually start with a capitalized word
        parts = line.split(maxsplit=1)
        command = parts[0]
        
        known_commands = [
            'Class', 'BaseType', 'LinkedSockets', 'Sockets', 'SocketGroup', 
            'ItemLevel', 'DropLevel', 'Quality', 'Rarity', 'SetBorderColor', 
            'SetTextColor', 'SetBackgroundColor', 'SetFontSize', 'PlayAlertSound', 
            'PlayAlertSoundPositional', 'CustomAlertSound', 'MinimapIcon', 
            'PlayEffect', 'DisableDropSound', 'EnableDropSound', 'Corrupted',
            'Identified', 'Fractured', 'Synthesised', 'AnyEnchantment', 'HasEnchantment',
            'Continue'
        ]
        
        # Operators like =, <, > might be attached or separated. We just do a loose check on the command name.
        # Removing operators for command extraction:
        clean_command = re.sub(r'[^a-zA-Z]', '', command)
        
        if clean_command and clean_command not in known_commands:
            # It might be a complex expression, or we might just warn
            # PoE filters are forgiving but we can flag completely unknown starts
            # To avoid false positives on valid complex strings, we just check if it matches basic knowns
            # Actually, to be safe and not over-block, we just check if it starts with a known command.
            is_known = any(line.startswith(kc) for kc in known_commands)
            if not is_known:
                errors.append(f"Line {i+1}: Unknown command or syntax error: '{line}'")
                
    return errors
