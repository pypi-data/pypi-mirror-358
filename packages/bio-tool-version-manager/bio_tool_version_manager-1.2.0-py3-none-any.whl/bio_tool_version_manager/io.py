# -*- coding: utf-8 -*-

import json
from typing import Dict

def write_json_file(data: Dict, file_path: str) -> None:
    """
    Writes python dictionary into json file specified by path
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"File was saved: {file_path}")
    except Exception as e:
        print(f"Error occured: {e}")
        
def load_json(json_file_path: str) -> Dict:
    """Load json from file path."""
    with open(json_file_path, 'r') as f:
        return json.load(f)