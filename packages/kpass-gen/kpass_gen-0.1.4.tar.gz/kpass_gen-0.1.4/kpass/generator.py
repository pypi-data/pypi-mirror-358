# Password generator itself

import itertools
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import os

# Ciphers dictionary to replace letters
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


# Function to apply ciphers to text
def aplly_ciphers(text):
    return ''.join(ciphers.get(char, char) for char in text)

# Function to generate passwords

def generator(name, age, birth_date):
    day, month, yaer = birth_date.split("/")

    name_tiny = name.lower().replace(" ", "")
    name_capital = name.upper().replace(" ", "")

    parts_name = name.split()
    first = parts_name[0]
    middle = "".join(parts_name[1:-1]) if len(parts_name) > 2 else ""
    last = parts_name[-1] if len(parts_name) > 1 else ""

    age_reversed  = age[::-1]

    base_combinations = [
        name_tiny, name_capital, first, middle, last,
        day, month, yaer,
        age, age_reversed,
        aplly_ciphers(name_tiny), aplly_ciphers(first), aplly_ciphers(last)
    ]

    base_combinations = list(set(filter(lambda x: x.strip() != "", base_combinations)))

    possible_passwords = set()

    # Calcula o total de combinações pra progress bar
    total = sum(len(list(itertools.permutations(base_combinations, i))) for i in range(2, 5))

    with Progress(
        TextColumn("[cyan]Generating passwords..."),
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("passwords", total=total)

        for i in range(2, 5):
            for combo in itertools.permutations(base_combinations, i):
                password = "".join(combo)
                if 6 <= len(password) <= 18:
                    possible_passwords.add(password)
                progress.update(task, advance=1)
                
    return  save_to_txt(list(possible_passwords))
    
    

# Function to save passwords to file

def save_to_txt(passwords, file_name="pass_generated.txt"):
    path = "passwords_generator"
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, file_name), "w", encoding="utf-8-sig") as file:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:

            tarefa = progress.add_task("[cyan]Saving passwords...", total=len(passwords))

            for password in passwords:
                file.write(password + "\n")
                progress.update(tarefa, advance=1)
