import json
from json_repair import repair_json

def slice_json_content(string):
    """Extrai JSON de uma string que pode conter markdown"""
    # Procurar por blocos de código JSON
    patterns = [
        ("```json\n", "\n```"),
        ("```json", "```"),
        ("```\n", "\n```"),
        ("```", "```")
    ]
    
    for start_pattern, end_pattern in patterns:
        start_index = string.find(start_pattern)
        if start_index != -1:
            start_index += len(start_pattern)
            end_index = string.find(end_pattern, start_index)
            if end_index != -1:
                return string[start_index:end_index].strip()
            
    bracket_patterns = [
        ("{", "}"),
        ("[", "]")
    ]
    
    start_end_options = []    
    for start_bracket, end_bracket in bracket_patterns:
        start_index = string.find(start_bracket)
        if start_index != -1:
            end_index = string.find(end_bracket, start_index)
            if end_index != -1:
                start_end_options.append((start_index, end_index + 1))
                
    # get with longest range
    if start_end_options:
        start_index, end_index = max(start_end_options, key=lambda x: x[1] - x[0])
        return string[start_index:end_index].strip()
            
    
            
    
    # Se não encontrou padrões, retornar a string original
    return string.strip()

def get_json_from_string(string):
    """Extrai e repara JSON de uma string"""
    json_content = slice_json_content(string)
    if not json_content:
        return None
    
    try:
        return json.loads(json_content)
    except json.JSONDecodeError:
        repaired_json = repair_json(json_content)
        if repaired_json:
            try:
                return json.loads(repaired_json)
            except json.JSONDecodeError:
                return None
        return None