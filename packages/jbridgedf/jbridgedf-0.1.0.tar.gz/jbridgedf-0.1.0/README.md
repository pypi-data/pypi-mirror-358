# JBridgeDF

**Bridge JSON APIs into clean, time-aware DataFrames.**

`JBridgeDF` is a lightweight Python library that simplifies the process of retrieving and transforming JSON data from APIs into tidy `pandas` DataFrames — ready for analysis or time series modeling.

## 🚀 Features

- Handles HTTP requests and error logging
- Parses JSON responses into clean DataFrames
- Handles different JSON answers: plain dict, list of dicts, key-word dict
- Filters out metadata
- Automatically removes inconsistent or empty columns
- Converts timestamps and standardizes time frequency (daily, monthly, quarterly)
- Designed for public data APIs (like Central Bank, IBGE, FRED, etc.)

## 📦 Installation

```bash
pip install -e .
```

## 🧪 Example Usage

```python
from jbridgedf.parser import APIDataParser

parser = APIDataParser()
df = parser.get_from_api(
    url="https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json",
    variable_list=["data", "valor"],
    is_list=True,
    frequency="monthly",
    date_as_index=True
)
print(df.head())
```

## 📁 Project Structure

- `jbridgedf/`: core library code
- `tests/`: unit tests (pytest recommended)
- `examples/`: real-world examples and demos

## 📬 Contact

For questions, suggestions, or contributions, open an [issue on GitHub](https://github.com/ODenteAzul/jbridgedf/issues) or email at **luismoraes.datascience@gmail.com**.

## 🤝 Ethical Use

This library was developed with the intention of supporting researchers, analysts, and developers working with open or public data APIs.

If you plan to use `JBridgeDF` in commercial applications, redistributed packages, or mission-critical systems, you are kindly encouraged to retain the original context, acknowledge the author, and consider contributing back.

This is not a legal restriction, but a request to respect the original purpose and community spirit of the project.

## 📄 License

MIT
