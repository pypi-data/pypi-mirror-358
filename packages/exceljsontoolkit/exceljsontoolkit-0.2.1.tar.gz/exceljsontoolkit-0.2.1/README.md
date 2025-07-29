# Excel JSON Toolkit

Excel JSON Toolkit is a Python package that allows you to:

- Extract structured JSON data from Excel files using OpenAI's LLMs.

- Load JSON files into Python dictionaries.

- Analyze and generate context maps describing the contents and dependencies of JSON files.

## 📦 Installation
```bash
pip install exceljsontoolkit
```
> Note: Requires Python 3.7+

## 🔧 Requirements

- pandas

- openai

- python-dotenv

These will be automatically installed with the package.

You also need to create a `.env` file with your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_key_here
```
## 🧠 Features

#### ✅ Extract Structured JSON from Excel

Uses OpenAI's GPT model to clean, extract, and standardize tabular data from Excel sheets into well-structured JSON files.

```python
from exceljsontoolkit import StructuredDataExtractor

extractor = StructuredDataExtractor(output_dir="output", model="gpt-4o-mini")
extractor.extract("your_excel_file.xlsx")
```

#### ✅ Load JSON Files

Loads JSON files and returns them as a dictionary.
```python
from exceljsontoolkit import LoadJsonFiles

loader = LoadJsonFiles()
data = loader.load_json_files("output/sheet1.json")
```
#### ✅ Generate Context Map

Analyzes JSON structure and relationships between files.
```python
from exceljsontoolkit import GenerateJsonContextMap

mapper = GenerateJsonContextMap()
context = mapper.generate_json_context_map(data)
print(context)
```
## 📁 Example Folder Structure
```
my_project/
├── your_excel_file.xlsx
├── output/
│   ├── Sheet1.json
├── .env
```
## 📃 License

This project is licensed under the MIT License.

## Authors

Developed by Basil Yaqoob  
Documented by Mahdi Jaffery