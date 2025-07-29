import json
import os

class LoadJsonFiles:
    """
    This class loads JSON files from a specified folder and returns a dictionary
    where the key is the filename (without extension) and the value is the JSON content.
    """
    
    def __init__(self):
        pass
    def load_json_files(self,filename: str) -> dict:
        """
        Load the JSON file in the folder and return a dictionary
        where key = filename (without extension), value = JSON content.
        """
        json_data = {}
        
        if filename.endswith(".json"):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    json_data[os.path.splitext(filename)[0]] = data
            except Exception as e:
                print(f"[✖] Failed to load {filename}: {e}")
        return json_data