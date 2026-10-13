Rekomendowana struktura
1. Schemat i słowniki
sql
CREATE SCHEMA IF NOT EXISTS portfolio;

CREATE TABLE IF NOT EXISTS portfolio.instruments (
    instrument_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker            TEXT NOT NULL UNIQUE,
    yfinance_ticker   TEXT,
    name              TEXT,
    asset_class       TEXT NOT NULL,
    instrument_type   TEXT NOT NULL,
    exchange          TEXT,
    currency          TEXT NOT NULL,
    country           TEXT,
    sector            TEXT,
    industry          TEXT,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS portfolio.data_sources (
    data_source_id   SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name      TEXT NOT NULL UNIQUE,
    source_url       TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS portfolio.calculation_runs (
    run_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_name         TEXT,
    data_source_id   SMALLINT NOT NULL REFERENCES portfolio.data_sources(data_source_id),
    price_currency   TEXT NOT NULL,
    period_start     DATE,
    period_end       DATE,
    return_frequency TEXT NOT NULL DEFAULT 'daily',
    annualization_factor INTEGER NOT NULL DEFAULT 252,
    min_periods      INTEGER NOT NULL DEFAULT 252,
    script_version   TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
asset_class warto trzymać jako kontrolowaną wartość: equity, etf, fund, bond, cash. instrument_type: np. common_stock, adr, ucits_etf, open_end_fund, government_bond_fund.

2. Ceny dzienne
sql
CREATE TABLE IF NOT EXISTS portfolio.daily_prices (
    instrument_id   INTEGER NOT NULL REFERENCES portfolio.instruments(instrument_id),
    price_date      DATE NOT NULL,
    data_source_id  SMALLINT NOT NULL REFERENCES portfolio.data_sources(data_source_id),
    open_price      NUMERIC(20, 8),
    high_price      NUMERIC(20, 8),
    low_price       NUMERIC(20, 8),
    close_price     NUMERIC(20, 8) NOT NULL,
    adjusted_close  NUMERIC(20, 8),
    volume          NUMERIC(20, 4),
    currency        TEXT NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (instrument_id, price_date, data_source_id)
);

CREATE INDEX IF NOT EXISTS idx_daily_prices_date
    ON portfolio.daily_prices (price_date);

CREATE INDEX IF NOT EXISTS idx_daily_prices_instrument_date
    ON portfolio.daily_prices (instrument_id, price_date DESC);
To jest wariant klasycznej tabeli OHLCV: unikalność zapewniana przez (instrument_id, price_date, data_source_id) chroni przed duplikatami, a adjusted_close pozwala rozdzielić ceny surowe od skorygowanych o dywidendy/splity.

3. Stopy zwrotu
sql
CREATE TABLE IF NOT EXISTS portfolio.daily_returns (
    instrument_id     INTEGER NOT NULL REFERENCES portfolio.instruments(instrument_id),
    return_date       DATE NOT NULL,
    price_currency    TEXT NOT NULL,
    return_type       TEXT NOT NULL,
    return_value      DOUBLE PRECISION NOT NULL,
    calculation_run_id BIGINT NOT NULL REFERENCES portfolio.calculation_runs(run_id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (instrument_id, return_date, price_currency, return_type, calculation_run_id)
);

CREATE INDEX IF NOT EXISTS idx_daily_returns_date
    ON portfolio.daily_returns (return_date);
return_type używałbym jako kontrolowanej wartości:

simple_local — prosty zwrot w walucie notowania,

simple_pln — prosty zwrot po przeliczeniu na PLN,

log_local,

log_pln.

Dla Twoich celów najważniejsze będą simple_local oraz simple_pln, bo pierwsza odpowiada analizie pojedynczego instrumentu, a druga realnej ekspozycji portfela w złotówkach.

4. Zmienność
sql
CREATE TABLE IF NOT EXISTS portfolio.volatility_metrics (
    calculation_run_id  BIGINT NOT NULL REFERENCES portfolio.calculation_runs(run_id),
    instrument_id       INTEGER NOT NULL REFERENCES portfolio.instruments(instrument_id),
    return_type         TEXT NOT NULL,
    metric_name         TEXT NOT NULL,
    metric_value        DOUBLE PRECISION NOT NULL,
    window_days         INTEGER NOT NULL,
    annualization_factor INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (
        calculation_run_id,
        instrument_id,
        return_type,
        metric_name,
        window_days
    )
);
Przykładowe metric_name:

daily_std,

annualized_volatility,

rolling_63d_annualized_volatility,

rolling_252d_annualized_volatility.

Dzięki temu nie musisz dodawać nowej kolumny przy każdym nowym wskaźniku.

5. Korelacje — wariant rekomendowany
sql
CREATE TABLE IF NOT EXISTS portfolio.correlation_pairs (
    calculation_run_id   BIGINT NOT NULL REFERENCES portfolio.calculation_runs(run_id),
    return_type          TEXT NOT NULL,
    correlation_method   TEXT NOT NULL,
    instrument_id_a      INTEGER NOT NULL REFERENCES portfolio.instruments(instrument_id),
    instrument_id_b      INTEGER NOT NULL REFERENCES portfolio.instruments(instrument_id),
    window_days          INTEGER NOT NULL,
    min_periods          INTEGER NOT NULL,
    correlation_value    DOUBLE PRECISION NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (
        calculation_run_id,
        return_type,
        correlation_method,
        instrument_id_a,
        instrument_id_b,
        window_days
    ),

    CONSTRAINT chk_corr_range CHECK (
        correlation_value >= -1 AND correlation_value <= 1
    ),
    CONSTRAINT chk_no_self_pair CHECK (
        instrument_id_a <> instrument_id_b
    )
);

CREATE INDEX IF NOT EXISTS idx_corr_pairs_a
    ON portfolio.correlation_pairs (instrument_id_a, return_type, correlation_method);

CREATE INDEX IF NOT EXISTS idx_corr_pairs_b
    ON portfolio.correlation_pairs (instrument_id_b, return_type, correlation_method);
Zasada: zapisuj tylko pary a < b, np. HOYA–GEA, ale nie GEA–HOYA. To eliminuje duplikaty i połowę wierszy.

6. Opcjonalnie: pełne macierze jako JSONB
Jeśli chcesz zachować dokładny artefakt z pandas — tak jak obecny CSV — dodaj tabelę archiwum:

sql
CREATE TABLE IF NOT EXISTS portfolio.correlation_matrices (
    calculation_run_id  BIGINT NOT NULL REFERENCES portfolio.calculation_runs(run_id),
    return_type         TEXT NOT NULL,
    correlation_method  TEXT NOT NULL,
    window_days         INTEGER NOT NULL,
    matrix_json         JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (
        calculation_run_id,
        return_type,
        correlation_method,
        window_days
    )
);
To nie zastępuje correlation_pairs, tylko ją uzupełnia. correlation_pairs jest do zapytań SQL, a matrix_json do audytu i odtworzenia dokładnego wyniku.

Przykładowe dane
sql
INSERT INTO portfolio.data_sources (source_name, source_url)
VALUES ('Yahoo Finance', 'https://finance.yahoo.com')
ON CONFLICT (source_name) DO NOTHING;

INSERT INTO portfolio.instruments
    (ticker, yfinance_ticker, name, asset_class, instrument_type, exchange, currency, country, sector, industry)
VALUES
    ('HOYA', '7741.T', 'HOYA Corporation', 'equity', 'common_stock', 'TSE', 'JPY', 'JP', 'Healthcare', 'Medical Devices'),
    ('GEA', 'G1A.DE', 'GEA Group AG', 'equity', 'common_stock', 'XETRA', 'EUR', 'DE', 'Industrials', 'Machinery'),
    ('HAPAG', 'HLAG.DE', 'Hapag-Lloyd AG', 'equity', 'common_stock', 'XETRA', 'EUR', 'DE', 'Industrials', 'Marine Shipping'),
    ('INDUS', 'INH.DE', 'INDUS Holding AG', 'equity', 'common_stock', 'XETRA', 'EUR', 'DE', 'Industrials', 'Industrial Holding'),
    ('CBF', 'CBF.WA', 'Cyber_Folks S.A.', 'equity', 'common_stock', 'GPW', 'PLN', 'PL', 'Technology', 'Internet Services'),
    ('NWAI', 'NWA.WA', 'NWAI Dom Maklerski S.A.', 'equity', 'common_stock', 'GPW', 'PLN', 'PL', 'Financials', 'Investment Banking'),
    ('SCW', 'SCW.WA', 'Scanway S.A.', 'equity', 'common_stock', 'GPW', 'PLN', 'PL', 'Technology', 'Optical Instruments'),
    ('XTB', 'XTB.WA', 'XTB S.A.', 'equity', 'common_stock', 'GPW', 'PLN', 'PL', 'Financials', 'Capital Markets'),
    ('KRU', 'KRU.WA', 'Kruk S.A.', 'equity', 'common_stock', 'GPW', 'PLN', 'PL', 'Financials', 'Consumer Finance'),
    ('GAW', 'GAW.L', 'Games Workshop Group PLC', 'equity', 'common_stock', 'LSE', 'GBP', 'GB', 'Consumer Discretionary', 'Leisure Products'),
    ('IH2O', 'IE00B1TXK627', 'Water Fund', 'fund', 'open_end_fund', 'LSE', 'GBP', 'IE', 'Utilities', 'Water Infrastructure'),
    ('VGEM', 'VGEM.DE', 'Emerging Markets Government Bond', 'bond', 'government_bond_fund', 'XETRA', 'EUR', 'DE', 'Fixed Income', 'Emerging Market Debt')
ON CONFLICT (ticker) DO UPDATE SET
    yfinance_ticker = EXCLUDED.yfinance_ticker,
    name = EXCLUDED.name,
    updated_at = now();
Jak wpasować to w skrypt
Moduł `portfolio_db.py` udostępnia funkcje zapisu dla instrumentów, cen,
zwrotów, metryk zmienności, par korelacji i archiwalnych macierzy. Skrypt
`analiza_zmiennosc_korelacje.py` wywołuje je automatycznie po obliczeniu
wyników. Dane logowania są wczytywane z lokalnego pliku `.env`, a zmienna
środowiskowa `DATABASE_URL` może nadpisać domyślne połączenie.

Nazwa bazy danych to `postgres`. Lokalna konfiguracja w `portfolio_db.py` oraz
kontener z `docker-compose.yml` używają tej bazy. Przy własnym serwerze można
nadpisać połączenie, ustawiając `DATABASE_URL` na adres PostgreSQL kończący się
na `/postgres`.

Docker Compose uruchamia PostgreSQL 18 z trwałym wolumenem `postgres_data`.
Kontener udostępnia port `5433` na hoście, aby nie kolidować z lokalną
instancją PostgreSQL działającą na porcie `5432`. Dane logowania i nazwa bazy pochodzą z pliku `.env` w katalogu `Correlations`.
Plik `.env` jest wykluczony z Git i nie należy go dodawać do repozytorium.

Aby uruchomić kontener w PowerShell:

```powershell
cd "C:\Users\Mergr\Desktop\giełda\Correlations"
docker compose up -d
docker compose ps
```

Poczekaj, aż stan kontenera będzie `healthy`. Skrypt uruchamiany na hoście
automatycznie wczyta poświadczenia z `.env` i połączy się przez port `5433`.
Uruchom analizę:

```powershell
python .\analiza_zmiennosc_korelacje.py
```

Jeśli chcesz nadpisać konfigurację, ustaw zmienną `DATABASE_URL`. Hasło
wczytane z `.env` jest kodowane podczas budowania domyślnego adresu połączenia.
Przed pierwszym uruchomieniem zainstaluj zależności w tym samym środowisku
Pythona, którego używasz do analizy:
`python -m pip install -r requirements.txt`.

Zatrzymaj kontener bez usuwania danych poleceniem `docker compose down`.
Wolumen można usunąć poleceniem `docker compose down -v`; to nieodwracalnie
kasuje dane bazy.

Zapis do PostgreSQL jest transakcyjny: błąd połączenia lub zapisu jest
zgłaszany, a częściowy przebieg nie zostaje zatwierdzony. Pliki CSV nadal są
generowane jako eksport wyników. Każde uruchomienie tworzy osobny
`calculation_run`, a `calculation_run_id` zachowuje historię zwrotów.
PostgreSQL przechowuje wyniki `simple_local` i `log_local`. Zwroty PLN wymagają
danych FX, które pozostają osobnym, przyszłym rozszerzeniem.

Co bym dodał później
portfolio.portfolios i portfolio.portfolio_positions — jeśli zaczniesz śledzić realne wagi, daty zakupu i dopłaty.

portfolio.fx_rates — kursy PLN/EUR, PLN/GBP, PLN/JPY, PLN/USD, żeby liczyć zwroty w PLN bez mieszania danych z Yahoo.

portfolio.portfolio_risk_metrics — zmienność, VaR, max drawdown i udział ryzyka poszczególnych pozycji.

Widoki SQL — np. v_latest_correlations_pearson_pln, żeby nie pisać za każdym razem złożonego zapytania.

Najważniejsza decyzja architektoniczna: nie zapisuj macierzy jako szerokiej tabeli. Zapisuj pary w correlation_pairs, a macierz jako JSONB tylko jako kopię audytową. Przy 10 instrumentach różnica jest kosmetyczna, ale przy 50–100 instrumentach i wielu okresach obliczeniowych długie wiersze stają się dużo łatwiejsze do filtrowania, wersjonowania i analizy.