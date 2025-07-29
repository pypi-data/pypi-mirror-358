class GenerateJsonContextMap:
    """
    This class generates a context map for JSON files in a specified folder.
    It analyzes the contents of each JSON file and summarizes the structure and dependencies."""
    def __init__(self):
        pass
    def generate_json_context_map(self,json_data: dict) -> list:
        """
        Analyzes each JSON file's contents and generates a context summary.
        Returns a list of dictionaries, each with keys: 'file', 'description', 'depends_on'.
        """
        context_list = []

        for filename, content in json_data.items():
            keys = list(content[0].keys()) if isinstance(content, list) and content else list(content.keys())
            
            # Basic description
            description = f"Contains structured data with fields: {', '.join(keys[:10])}"

            # Guess dependencies
            depends_on = []
            for other_filename, other_content in json_data.items():
                if other_filename == filename:
                    continue
                other_keys = list(other_content[0].keys()) if isinstance(other_content, list) and other_content else list(other_content.keys())
                if any(k in other_keys for k in keys):
                    depends_on.append(other_filename)

            context_list.append({
                "file": filename,
                "description": description,
                "depends_on": depends_on
            })

        return context_list
