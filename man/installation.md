# Slovensky
## Inštalačná príručka k WSQ Editor
### Prerekvizity
- Python 3 (s nainštalovaným modulom `tkinter` - napr. `sudo apt-get install python3.7-tk`)
- príslušný inštalátor balíčkov pip
- internetové pripojenie

Všetky ostatné moduly a knižnice budú doinštalované v ďalších krokoch.

### Linux a macOS
Presuňte sa do priečinku `src` obsahujúceho Python zdrojové súbory aplikácie. V príkazovom riadku terminálu spustite:

- `python3 -m venv <cesta pre novy priecinok prostredia>`
- `source cesta/k/venv/bin/activate`
- `python -m pip install -r requirements.txt`

### Windows
Presuňte sa do priečinku `src` obsahujúceho Python zdrojové súbory aplikácie. V prostredí Windows PowerShell spustite:

- `python3 -m venv <cesta pre novy priecinok prostredia>`
- `.\cesta\k\venv\Scripts\activate`
- `python -m pip install -r requirements.txt`

# Spustenie aplikácie
V prípade, že bolo využité venv virtuálne prostredie pri inštalácii, aktivujte ho pred spustením aplikácie pomocou
príkazu `source cesta/k/venv/bin/activate` na Linux a macOS systémoch alebo príkazom `.\cesta\k\venv\Scripts\activate`
na Windows systémoch.
Presuňte sa do priečinku so zdrojovým súborom `app.py` a spustite aplikáciu pomocou `python app.py`.

# English
## Installation guide for WSQ Editor
### Prerequisites
- Python 3 (with the `tkinter` module installed - e.g. `sudo apt-get install python3.7-tk`)
- the corresponding pip package installer
- an internet connection

All the other needed modules and libraries will be installed in the next steps.

### Linux and macOS
Navigate to the `src` folder containing the Python source files. In the terminal command line run:

- `python3 -m venv <path to new virtual environment>`
- `source path/to/venv/bin/activate`
- `python -m pip install -r requirements.txt`

### Windows
Navigate to the `src` folder containing the Python source files. In Windows PowerShell run:

- `python3 -m venv <path to new virtual environment>`
- `.\path\to\venv\Scripts\activate`
- `python -m pip install -r requirements.txt`

## Running the application
In case the virtual environment has been used during the app installation, activate it before launching the application
using `source path/to/venv/bin/activate` on Linux and macOS or using `.\path\to\venv\Scripts\activate` on Windows.
Navigate to the folder with the source file `app.py` and launch it using `python app.py`.
