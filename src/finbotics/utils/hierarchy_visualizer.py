# src/finbotics/utils/hierarchy_visualizer.py
from typing import Dict, Any
import json

class HierarchyVisualizer:
    """Visualize hierarchical financial data"""
    
    @staticmethod
    def print_tree(tree: Dict[str, Any], indent: int = 0):
        """Print hierarchy tree structure"""
        for key, value in tree.items():
            print('  ' * indent + key)
            if value['data']:
                data = value['data']
                values = json.loads(data['values_json'])
                if values:
                    sample_value = list(values.values())[0]
                    print('  ' * (indent + 1) + f"Value: ${sample_value:,.2f}")
            if value['children']:
                HierarchyVisualizer.print_tree(value['children'], indent + 1)
    
    @staticmethod
    def export_to_json(tree: Dict[str, Any], output_file: str):
        """Export hierarchy to JSON file"""
        def clean_tree(node):
            cleaned = {}
            for key, value in node.items():
                cleaned[key] = {
                    'data': value['data'] if value['data'] else None,
                    'children': clean_tree(value['children']) if value['children'] else {}
                }
            return cleaned
        
        cleaned_tree = clean_tree(tree)
        with open(output_file, 'w') as f:
            json.dump(cleaned_tree, f, indent=2, default=str)