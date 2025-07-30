# kpass

**kpass** is a Python library that:

1. Generates hundreds (or thousands) of password combinations based on a person’s full name, age, and date of birth.  
2. Applies “leet”-style substitutions (e.g., A → 4, S → $, E → 3).  
3. Calculates **password strength** according to length, digit presence, special characters, mixed case, and absence of simple numeric sequences.  
4. Automatically saves generated passwords to a `.txt` file with progress bars powered by the `rich` library.

---

## 📦 Installation

```bash
pip install kpass-gen
````

---

## 🚀 Example Usage

### 1. Generating Passwords

```python
from kpass import generator

# Generate hundreds of password combinations based on personal data
generator(
    name="Johnny Silverhand",
    age="34",
    birth_date="16/11/1988"
)
```

> This will create a file named `pass_generated.txt` (in the default or specified folder) containing all valid passwords between 6 and 18 characters, with a progress bar shown during generation.

---

### 2. Applying Leet-Style Substitutions

```python
from kpass import aplly_ciphers

original = "SecurePass"
leet = aplly_ciphers(original)
print(leet)  # → "$3cur3P4$$" (example)
```

---

### 3. Saving Passwords Manually

If you already have a list of passwords and only want to save them:

```python
from kpass import save_to_txt

passwords = ["abc123!", "Johnny34@", "4bcc!23"]
save_to_txt(passwords, file_name="my_passwords.txt")
```

---

### 4. Checking Password Strength

```python
from kpass import verify

# Returns a numeric score (0–6)
score = verify(password="Luc@s683", want_verdict=False)
print(score)        # → 6

# Returns a hashtag verdict
label = verify(password="Luc@s683", want_verdict=True)
print(label)        # → "#very_strong"
```

| Score | Verdict       | Description |
| :---: | :------------ | :---------- |
|   0   | #very\_weak   | Very weak   |
|  1–2  | #weak         | Weak        |
|   3   | #mean         | Average     |
|   4   | #good         | Good        |
|   5   | #strong       | Strong      |
|   6   | #very\_strong | Very strong |

---

## 🔧 API Reference

```python
generator(
    name: str,
    age: str,
    birth_date: str
) -> None
```

* **Generates** and **saves** password combinations automatically to `pass_generated.txt`.

```python
aplly_ciphers(
    text: str
) -> str
```

* **Transforms** the input text using leet-style substitutions defined in the internal dictionary.

```python
save_to_txt(
    passwords: list[str],
    file_name: str = "pass_generated.txt"
) -> None
```

* **Saves** the list of passwords to a text file, displaying a progress bar in the terminal.

```python
verify(
    password: str,
    want_verdict: bool = True
) -> int | str
```

* **Evaluates** the strength of a password: returns a numeric score (0–6) or, if `want_verdict=True`, the corresponding hashtag verdict.

---

## ✅ Requirements

* Python 3.6 or higher
* `rich`

---

## 📄 License

This project is licensed under the MIT License.