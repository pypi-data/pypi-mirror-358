# kpass 

**kpass** is a Python library that generates hundreds (or thousands) of password combinations based on a person's full name, age, and date of birth.

It also includes `leet`-style substitutions (e.g., A → 4, S → $, E → 3), and automatically saves the generated passwords to a `.txt` file with progress bars using the `rich` library.

---

## 📦 Installation

```bash
pip install kpass-gen
```
---

🚀 Example usage


```python
from kpass import generator

# Generate passwords based on personal data
generator(
    name="Jhonny Silverhand",
    age="34",
    birth_date="16/11/1988"
)
```

This will create a folder called passwords_generator containing a file named pass_generated.txt with valid password combinations between 6 and 18 characters.


---

🔧 Available functions

generator(name: str, age: str, birth_date: str) -> bool

Generates and saves passwords automatically.

aplly_ciphers(text: str) -> str

Applies leet-style substitutions to the given text (e.g., A → 4, S → $, etc.).

save_to_txt(passwords: list[str], file_name: str = "pass_generated.txt")

Saves a list of passwords to a .txt file with a progress bar.


---

✅ Requirements

Python 3.6 or higher

rich


---

📄 License

This project is licensed under the MIT License.



