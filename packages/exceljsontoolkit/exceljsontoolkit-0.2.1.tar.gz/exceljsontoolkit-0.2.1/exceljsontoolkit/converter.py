import pandas as pd
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

class StructuredDataExtractor:
    def __init__(self, output_dir="structured_output", model="gpt-4o"):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.output_dir = output_dir
        self.model = model
        os.makedirs(self.output_dir, exist_ok=True)

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        return df.to_markdown(index=False)

    def _clean_json_string(self, output: str) -> str:
        lines = output.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().endswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()

    def _process_sheet(self, sheet_name: str, df: pd.DataFrame) -> None:
        prompt = f"""
You are a data analyst. The following table is from a sheet named '{sheet_name}' in an Excel file.
Your task is to:
1. Remove irrelevant rows or columns.
2. Convert the relevant data into structured JSON format.
3. If data is inconsistent, use your best guess to standardize it.

Data:
{self._dataframe_to_markdown(df)}

Return only the final structured JSON. Do not explain anything.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            raw_output = response.choices[0].message.content.strip()
            cleaned_json = self._clean_json_string(raw_output)
            output_path = os.path.join(self.output_dir, f"{sheet_name}.json")

            try:
                parsed = json.loads(cleaned_json)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)
            except json.JSONDecodeError:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_json)

            print(f"Saved {output_path}")
        except Exception as e:
            print(f"Error processing '{sheet_name}': {e}")

    def extract(self, excel_file: str) -> None:
        try:
            sheets = pd.read_excel(excel_file, sheet_name=None)
        except Exception as e:
            print(f"Failed to read Excel file: {e}")
            return

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._process_sheet, name, df)
                for name, df in sheets.items()
            ]
            for future in as_completed(futures):
                pass
