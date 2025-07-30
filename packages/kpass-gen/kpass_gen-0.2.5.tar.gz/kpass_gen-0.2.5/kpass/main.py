import itertools
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import re
import string
import json
from math import perm
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# Ciphers dictionary to replace letters with leetspeak equivalents
# Each key is a character and the corresponding value is its cipher substitution
# -----------------------------------------------------------------------------

ciphers = {
    "A": "4", "a": "4", "Á": "4", "á": "4", "@": "4",
    "B": "8", "b": "8",
    "C": "(", "c": "(",
    "D": "[)", "d": "[)",
    "E": "3", "e": "3", "É": "3", "é": "3", "&": "3",
    "F": "#", "f": "#",
    "G": "6", "g": "6",
    "H": "#", "h": "#",
    "I": "1", "i": "1", "Í": "1", "í": "1", "!": "1",
    "J": "_|", "j": "_|",
    "K": "|<", "k": "|<",
    "L": "1", "l": "1",
    "M": "/\\/\\", "m": "/\\/\\",
    "N": "|\\|", "n": "|\\|",
    "O": "0", "o": "0", "Ó": "0", "ó": "0",
    "P": "|D", "p": "|D",
    "Q": "0_", "q": "0_",
    "R": "12", "r": "12",
    "S": "$", "s": "$", "Š": "$", "š": "$",
    "T": "7", "t": "7",
    "U": "(_)", "u": "(_)",
    "V": "\\/", "v": "\\/",
    "W": "\\/\\/", "w": "\\/\\/",
    "X": "%", "x": "%",
    "Y": "`/", "y": "`/",
    "Z": "2", "z": "2"
}

# -----------------------------------------------------------------------------
# Function: apply_ciphers
# Description:
#   Transforms input text by replacing each character according to the ciphers dict
# Parameters:
#   text (str): The original text to be ciphered
# Returns:
#   str: The transformed text with cipher substitutions
# -----------------------------------------------------------------------------

def apply_ciphers(text: str) -> str:
    return ''.join(ciphers.get(char, char) for char in text)

# -----------------------------------------------------------------------------
# Utility: write with progress bar
# -----------------------------------------------------------------------------

def _write_with_progress(write_fn, items):
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Saving passwords...", total=len(items))
        for item in items:
            write_fn(item)
            progress.update(task, advance=1)

# -----------------------------------------------------------------------------
# Function: save_to_file
# Description:
#   Writes a list of passwords, scores, and verdicts to a file with progress
# Parameters:
#   passwords (list[str]): List of password strings
#   scores (list[int]): Corresponding strength scores
#   verdicts (list[str]): Corresponding verdict strings
#   file_name (str): Output filename without extension
#   file_type (str): Extension (json, csv, yaml, yml)
# Returns:
#   None
# -----------------------------------------------------------------------------

def save_to_file(
    passwords: list[str],
    scores: list[int],
    verdicts: list[str],
    file_name: str = "pass_generated",
    file_type: str = "json"
) -> None:
    extension = file_type.lstrip('.')
    path = Path(f"{file_name}.{extension}")
    path.write_text("", encoding="utf-8-sig")  # limpa conteúdo existente

    def writer_json(item):
        pwd, score, verdict = item
        return json.dumps({"password": pwd, "score": score, "veredict": verdict}, indent=4, ensure_ascii=False) + "\n"

    def writer_csv(item):
        pwd, score, verdict = item
        return (
            f'"password","{pwd}",\n'
            f'"score","{score}",\n'
            f'"veredict","{verdict}"\n\\n'
        )

    def writer_yaml(item):
        pwd, score, verdict = item
        return (
            f'"password": "{pwd}"\n'
            f'"score": "{score}"\n'
            f'"veredict": "{verdict}"\n\\n'
        )

    if extension == "json":
        writer = writer_json
    elif extension == "csv":
        writer = writer_csv
    elif extension in ("yaml", "yml"):
        writer = writer_yaml
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    items = list(zip(passwords, scores, verdicts))
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Saving passwords...", total=len(items))
        with path.open("a", encoding="utf-8-sig") as file:
            for item in items:
                file.write(writer(item))
                progress.update(task, advance=1)

# -----------------------------------------------------------------------------
# Function: base_files_architecture (no changes needed)
# -----------------------------------------------------------------------------
def base_files_architecture(password, score, verdict, file_type):
    if file_type.lower() in ("json", ".json"):
        return json.dumps({"password": password, "score": str(score), "veredict": verdict}, indent=4, ensure_ascii=False) + "\n\n"
    if file_type.lower() in ("csv", ".csv"):
        return (
            f'"password","{password}",\n'
            f'"score","{score}\n"'
            f'"veredict","{verdict}"\n'
        ) + "\n"
    if file_type.lower() in ("yaml", ".yaml", "yml", ".yml"):
        return (
            f'"password": "{password}"\n'
            f'"score": "{score}"\n'
            f'"veredict": "{verdict}"\n'
        ) + "\n"

# -----------------------------------------------------------------------------
# Function: generator
# Description:
#   Builds possible password permutations based on user info and ciphers,
#   filters by length, evaluates strength, and saves them
# -----------------------------------------------------------------------------

def generator(
    name: str,
    age: str,
    birth_date: str,
    file_type: str = "json",
    file_name: str = "pass_generated"
) -> None:
    dt = datetime.strptime(birth_date, "%d/%m/%Y")
    day, month, year = dt.strftime("%d"), dt.strftime("m"), dt.strftime("Y")
    name_tiny = name.lower().replace(" ", "")
    parts = name.split()
    first = parts[0]
    middle = "".join(parts[1:-1]) if len(parts) > 2 else ""
    last = parts[-1] if len(parts) > 1 else ""
    age_reversed = age[::-1]
    bases = [
        name_tiny, name.upper().replace(" ", ""), first, middle, last,
        day, month, year, age, age_reversed,
        apply_ciphers(name_tiny), apply_ciphers(first), apply_ciphers(last)
    ]
    bases = list({b for b in bases if b.strip()})
    possible_passwords = set()
    total = sum(perm(len(bases), r) for r in range(2, 5))
    with Progress(
        TextColumn("[cyan]Generating passwords..."),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("passwords", total=total)
        for length in range(2, 5):
            for combo in itertools.permutations(bases, length):
                pwd = "".join(combo)
                if 6 <= len(pwd) <= 18:
                    possible_passwords.add(pwd)
                progress.update(task, advance=1)
    scored = [(pwd, verify(pwd, False), veredict(verify(pwd, False))) for pwd in possible_passwords]
    passwords, scores, verdicts = zip(*scored)
    save_to_file(list(passwords), list(scores), list(verdicts), file_name, file_type)

# -----------------------------------------------------------------------------
# Sequence, verdict, and verify unchanged (except typo fix)
# -----------------------------------------------------------------------------

def check_sequences(password: str) -> bool:
    digits = [int(c) for c in password if c.isdigit()]
    for i in range(len(digits) - 2):
        if digits[i] + 1 == digits[i+1] == digits[i+2] - 1:
            return True
        if digits[i] - 1 == digits[i+1] == digits[i+2] + 1:
            return True
    return False

def veredict(score: int) -> str:
    levels = [
        "#very_weak", "#weak", "#weak", "#mean", "#good", "#strong", "#very_strong"
    ]
    return levels[score] if 0 <= score < len(levels) else "#unknown"

def verify(
    password: str,
    want_verdict: bool = True,
) -> int | str:
    strength = 0
    if len(password) >= 8:
        strength += 1
        if re.search(r'\d', password):
            strength += 1
            if any(c in string.punctuation for c in password):
                strength += 1
                if any(c.isupper() for c in password):
                    strength += 1
                if any(c.islower() for c in password):
                    strength += 1
                if not check_sequences(password):
                    strength += 1
    return veredict(strength) if want_verdict else strength