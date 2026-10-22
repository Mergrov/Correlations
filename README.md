VIBECODED.
Don't know what the end goal is going to be for this one.
For now it calculates correlations between any given number of stocks and saves data to a postgres instance and appropriate .csvs. Local env only for now.

TODO:
1. Fix postgres port discrepancies (local vs contenerized instance)
2. Add credential processing from .env (file in .gitignore - present only locally)
3. Refactor legacy, massive mappings from analiza_zmiennosci_korelacje.py to get the data from postgres
