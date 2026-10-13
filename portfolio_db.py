from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping, Sequence
from urllib.parse import quote

import pandas as pd


def _load_local_environment() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if name:
            os.environ.setdefault(name, value)


_load_local_environment()
DEFAULT_DATABASE_URL = (
    f"postgresql://{quote(os.getenv('POSTGRES_USER', 'postgres'), safe='')}:"
    f"{quote(os.getenv('POSTGRES_PASSWORD', ''), safe='')}@localhost:5433/"
    f"{quote(os.getenv('POSTGRES_DB', 'postgres'), safe='')}"
)

STOXX_Global_Secelt_div_100_full = {
    "Legal and general": "LGEN.L",
    "Aegon": "AEG",
    "investec": "INVP.L",
    "ABN Amro": "ABN.AS",
    "Natwest group": "NWG.L",
    "DBS group holdings": "D05.SI",
    "ASR NEDERLAND": "ASRNL.AS",
    "NN group": "NN.AS",
    "SUNCORP GROUP": "SUN.AX",
    "CREDIT AGRICOLE SA": "ACA.PA",
    "PRUDENTIAL FINANCIAL INC": "PRU",
    "POSTE ITALIANE": "PST.MI",
    "BNP PARIBAS SA": "BNP.PA",
    "HSBC HOLDINGS PLC": "HSBA.L",
    "ING GROEP": "INGA.AS",
    "T ROWE PRICE GROUP": "TROW",
    "AGEAS": "AGS.BR",
    "SCOR": "SCR.PA",
    "UNITED OVERSEAS BANK LTD": "U11.SI",
    "ALLIANZ": "ALV.DE",
    "AXA SA": "CS.PA",
    "BANK OF NOVA SCOTIA": "BNS.TO",
    "MANULIFE FINANCIAL": "MFC.TO",
    "SUN LIFE FINANCIAL INC": "SLF.TO",
    "POWER CORPORATION OF CANADA": "POW.TO",
    "ZURICH INSURANCE GROUP AG": "ZURN.SW",
    "DAIWA SECURITIES GROUP INC": "8601.T",
    "TRUIST FINANCIAL": "TFC",
    "US BANCORP": "USB",
    "BANK OF MONTREAL": "BMO.TO",
    "REGIONS FINANCIAL": "RF",
    "TORONTO DOMINION": "TD.TO",
    "PRINCIPAL FINANCIAL GROUP INC": "PFG",
    "NATIONAL AUSTRALIA BANK LTD": "NAB.AX",
    "HUNTINGTON BANCSHARES INC": "HBAN",
    "FIFTH THIRD BANCORP": "FITB",
    "CANADIAN IMPERIAL BANK OF COMMERCE": "CM.TO",
    "ROYAL BANK OF CANADA": "RY.TO",
    "CITIZENS FINANCIAL GROUP INC": "CFG",
    "FIDELITY NATIONAL FINANCIAL INC": "FNF",
    "NATIONAL BANK OF CANADA": "NA.TO",
    "SITC INTERNATIONAL HOLDINGS LTD": "1308.HK",
    "TELEPERFORMANCE": "TEP.PA",
    "B&M EUROPEAN VALUE RETAIL PLC": "BME.L",
    "AKER BP": "AKRBP.OL",
    "HP INC": "HPQ",
    "TAYLOR WIMPEY PLC": "TW.L",
    "WOODSIDE ENERGY GROUP LTD": "WDS.AX",
    "SIGNIFY": "LIGHT.AS",
    "BMW": "BMW.DE",
    "KAWASAKI KISEN LTD": "9107.T",
    "METCASH": "MTS.AX",
    "SWIRE PACIFIC LTD A": "SWRAY",
    "FORTESCUE LTD": "FMG.AX",
    "ORLEN": "PKN.WA",
    "PFIZER": "PFE",
    "CLP HOLDINGS": "0002.HK",
    "HONDA MOTOR": "7267.T",
    "CAPITALAND INTEGRATED COMMERCIAL T": "C38U.SI",
    "RUBIS": "RUI.PA",
    "POWER ASSETS HOLDINGS": "0006.HK",
    "HENDERSON LAND DEVELOPMENT LTD": "0012.HK",
    "COVIVIO SA": "COV.PA",
    "RIO TINTO LONDON": "RIO.L",
    "JAPAN TOBACCO": "2914.T",
    "WH GROUP": "0288.HK",
    "HARVEY NORMAN HOLDINGS LTD": "HVN.AX",
    "VERIZON COMMUNICATIONS INC": "VZ",
    "RIO TINTO AUSTRALIA": "RIO.AX",
    "TARGET CORP": "TGT",
    "MITSUI FUDOSAN LOGISTICS PARK REIT": "3471.T",
    "VOLKSWAGEN": "VOW3.DE",
    "CK ASSET HOLDINGS LTD": "1113.HK",
    "PHILLIPS 66": "PSX",
    "GENERAL MILLS INC": "GIS",
    "CONTACT ENERGY LTD": "CEN.NZ",
    "JB HI-FI LTD": "JBH.AX",
    "MAZDA MOTOR": "7261.T",
    "MERCEDES-BENZ GROUP N AG": "MBG.DE",
    "KOBE STEEL": "5406.T",
    "JFE HOLDINGS": "5411.T",
    "CHEVRON": "CVX",
    "CAPITALAND ASCENDAS REIT": "A17U.SI",
    "ORANGE SA": "ORA.PA",
    "EDISON INTERNATIONAL": "EIX",
    "XINYI GLASS HOLDINGS": "0868.HK",
    "ROGERS COMMUNICATIONS": "RCI-B.TO",
    "CONOCOPHILLIPS": "COP",
    "COMCAST CLASS A": "CMCSA",
    "SUN HUNG KAI PROPERTIES LTD": "0016.HK",
    "CONSOLIDATED EDISON": "ED",
    "AMGEN INC": "AMGN",
    "DUKE ENERGY CORP": "DUK",
    "DIAMONDBACK ENERGY": "FANG",
    "SOUTHERN": "SO",
    "INTERNATIONAL BUSINESS MACHINES": "IBM",
    "DEVON ENERGY": "DVN",
    "SEMPRA": "SRE",
    "GILEAD SCIENCES": "GILD",
    "ENTERGY CORP": "ETR",
}

Portfolio = {
    "Cyber_Folks": "CBF.WA",
    "Games Workshop": "GAW.L",
    "XTB": "XTB.WA",
    "NWAI": "NWA.WA",
    "Scanway": "SCW.WA",
    "Hoya": "7741.T",
    "Kruk": "KRU.WA",
    "USD denominated em bonds": "VGEM.DE",
    "STOXX Global Select Dividends": "ISPA.DE",
    "Global water": "IH2O.L",
}

SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS portfolio;

CREATE TABLE IF NOT EXISTS portfolio.instruments (
    instrument_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker            TEXT NOT NULL UNIQUE,
    yfinance_ticker   TEXT NOT NULL,
    name              TEXT,
    asset_class       TEXT,
    instrument_type   TEXT,
    exchange          TEXT NOT NULL,
    currency          TEXT NOT NULL,
    country           TEXT,
    sector            TEXT,
    industry          TEXT,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE portfolio.instruments
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

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

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'portfolio.daily_returns'::regclass
          AND contype = 'p'
          AND pg_get_constraintdef(oid) LIKE
              'PRIMARY KEY (instrument_id, return_date, price_currency, return_type, calculation_run_id)%'
    ) THEN
        ALTER TABLE portfolio.daily_returns
            DROP CONSTRAINT IF EXISTS daily_returns_pkey;
        ALTER TABLE portfolio.daily_returns
            ADD CONSTRAINT daily_returns_pkey PRIMARY KEY (
                instrument_id, return_date, price_currency, return_type, calculation_run_id
            );
    END IF;
END;
$$;

CREATE INDEX IF NOT EXISTS idx_daily_returns_date
    ON portfolio.daily_returns (return_date);

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
"""


def infer_listing(ticker: str) -> tuple[str, str]:
    suffix_listings = {
        ".WA": ("GPW", "PLN"),
        ".L": ("LSE", "GBP"),
        ".DE": ("XETRA", "EUR"),
        ".T": ("TSE", "JPY"),
        ".AS": ("EURONEXT_AMSTERDAM", "EUR"),
        ".PA": ("EURONEXT_PARIS", "EUR"),
        ".MI": ("BORSA_ITALIANA", "EUR"),
        ".BR": ("EURONEXT_BRUSSELS", "EUR"),
        ".OL": ("OSLO_BORS", "NOK"),
        ".AX": ("ASX", "AUD"),
        ".HK": ("HKEX", "HKD"),
        ".SI": ("SGX", "SGD"),
        ".TO": ("TSX", "CAD"),
        ".SW": ("SIX", "CHF"),
        ".NZ": ("NZX", "NZD"),
    }
    for suffix, listing in suffix_listings.items():
        if ticker.endswith(suffix):
            return listing
    return "UNKNOWN", "USD"


def get_connection(dsn: str | None = None):
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "psycopg is required to connect to PostgreSQL. Install it before running the database loader."
        ) from exc
    if dsn is None:
        dsn = os.getenv("DATABASE_URL")
        if dsn is None:
            dsn = DEFAULT_DATABASE_URL
    return psycopg.connect(dsn)


def initialize_database(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)


def ensure_data_source(conn, source_name: str, source_url: str | None = None) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO portfolio.data_sources (source_name, source_url)
            VALUES (%s, %s)
            ON CONFLICT (source_name) DO UPDATE SET source_url = EXCLUDED.source_url
            RETURNING data_source_id
            """,
            (source_name, source_url),
        )
        data_source_id = cur.fetchone()[0]
    return int(data_source_id)


def create_calculation_run(
    conn,
    run_name: str,
    data_source_id: int,
    price_currency: str,
    period_start: str | None = None,
    period_end: str | None = None,
    return_frequency: str = "daily",
    annualization_factor: int = 252,
    min_periods: int = 252,
    script_version: str | None = None,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO portfolio.calculation_runs (
                run_name, data_source_id, price_currency, period_start, period_end,
                return_frequency, annualization_factor, min_periods, script_version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING run_id
            """,
            (
                run_name,
                data_source_id,
                price_currency,
                period_start,
                period_end,
                return_frequency,
                annualization_factor,
                min_periods,
                script_version,
            ),
        )
        run_id = cur.fetchone()[0]
    return int(run_id)


def save_instruments(conn, instruments_df: pd.DataFrame) -> None:
    if instruments_df.empty:
        return

    required = {"ticker", "yfinance_ticker", "exchange", "currency"}
    missing = sorted(required.difference(instruments_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for instruments: {missing}")

    rows: list[tuple] = []
    for record in instruments_df.to_dict("records"):
        rows.append(
            (
                record.get("ticker"),
                record.get("yfinance_ticker"),
                record.get("name"),
                record.get("asset_class"),
                record.get("instrument_type"),
                record.get("exchange"),
                record.get("currency"),
                record.get("country"),
                record.get("sector"),
                record.get("industry"),
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO portfolio.instruments (
                ticker, yfinance_ticker, name, asset_class, instrument_type,
                exchange, currency, country, sector, industry
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                yfinance_ticker = EXCLUDED.yfinance_ticker,
                name = EXCLUDED.name,
                asset_class = EXCLUDED.asset_class,
                instrument_type = EXCLUDED.instrument_type,
                exchange = EXCLUDED.exchange,
                currency = EXCLUDED.currency,
                country = EXCLUDED.country,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                updated_at = now()
            """,
            rows,
        )


def seed_initial_instruments(conn, mappings: Sequence[Mapping[str, str]]) -> int:
    combined: dict[str, dict[str, str]] = {}
    fund_tickers = {"ISPA.DE", "IH2O.L"}
    bond_fund_tickers = {"VGEM.DE"}
    for mapping in mappings:
        for name, yfinance_ticker in mapping.items():
            if not yfinance_ticker:
                continue
            exchange, currency = infer_listing(str(yfinance_ticker))
            asset_class = (
                "bond" if yfinance_ticker in bond_fund_tickers
                else "etf" if yfinance_ticker in fund_tickers
                else "equity"
            )
            instrument_type = (
                "government_bond_fund" if yfinance_ticker in bond_fund_tickers
                else "ucits_etf" if yfinance_ticker in fund_tickers
                else "common_stock"
            )
            combined[str(yfinance_ticker)] = {
                "ticker": str(yfinance_ticker),
                "yfinance_ticker": str(yfinance_ticker),
                "name": str(name),
                "asset_class": asset_class,
                "instrument_type": instrument_type,
                "exchange": exchange,
                "currency": currency,
                "country": None,
                "sector": None,
                "industry": None,
            }

    with conn.cursor() as cur:
        cur.execute(
            "SELECT yfinance_ticker FROM portfolio.instruments WHERE yfinance_ticker IS NOT NULL"
        )
        existing = {row[0] for row in cur.fetchall()}

    records = [
        payload for yfinance_ticker, payload in combined.items() if yfinance_ticker not in existing
    ]
    if not records:
        return 0

    save_instruments(conn, pd.DataFrame(records))
    return len(records)


def resolve_instrument_ids(conn, tickers: Sequence[str]) -> Mapping[str, int]:
    if not tickers:
        return {}
    unique_tickers = list(dict.fromkeys(str(ticker) for ticker in tickers if str(ticker).strip()))
    if not unique_tickers:
        return {}

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT instrument_id, ticker, yfinance_ticker
            FROM portfolio.instruments
            WHERE ticker = ANY(%s) OR yfinance_ticker = ANY(%s)
            """,
            (unique_tickers, unique_tickers),
        )
        results = cur.fetchall()
        exact_tickers = {
            ticker: instrument_id
            for instrument_id, ticker, _ in results
            if ticker in unique_tickers
        }
        yfinance_tickers = {
            yfinance_ticker: instrument_id
            for instrument_id, _, yfinance_ticker in results
            if yfinance_ticker in unique_tickers
        }
        return {**yfinance_tickers, **exact_tickers}


def save_daily_prices(conn, prices_df: pd.DataFrame, data_source_id: int) -> None:
    if prices_df.empty:
        return

    required = {"ticker", "price_date", "close_price", "currency"}
    missing = sorted(required.difference(prices_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for daily_prices: {missing}")

    lookup = resolve_instrument_ids(conn, prices_df["ticker"].tolist())
    missing_tickers = sorted(set(prices_df["ticker"]) - set(lookup))
    if missing_tickers:
        raise ValueError(f"Unknown instruments in daily_prices: {missing_tickers}")
    rows: list[tuple] = []

    for record in prices_df.to_dict("records"):
        instrument_id = lookup.get(record.get("ticker"))
        rows.append(
            (
                instrument_id,
                record.get("price_date"),
                data_source_id,
                record.get("open_price"),
                record.get("high_price"),
                record.get("low_price"),
                record.get("close_price"),
                record.get("adjusted_close"),
                record.get("volume"),
                record.get("currency"),
            )
        )

    if not rows:
        return

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO portfolio.daily_prices (
                instrument_id, price_date, data_source_id, open_price, high_price,
                low_price, close_price, adjusted_close, volume, currency
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instrument_id, price_date, data_source_id) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                adjusted_close = EXCLUDED.adjusted_close,
                volume = EXCLUDED.volume,
                currency = EXCLUDED.currency,
                updated_at = now()
            """,
            rows,
        )


def save_daily_returns(conn, returns_df: pd.DataFrame, run_id: int) -> None:
    if returns_df.empty:
        return

    required = {"ticker", "return_date", "price_currency", "return_type", "return_value"}
    missing = sorted(required.difference(returns_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for daily_returns: {missing}")

    lookup = resolve_instrument_ids(conn, returns_df["ticker"].tolist())
    missing_tickers = sorted(set(returns_df["ticker"]) - set(lookup))
    if missing_tickers:
        raise ValueError(f"Unknown instruments in daily_returns: {missing_tickers}")
    rows: list[tuple] = []

    for record in returns_df.to_dict("records"):
        instrument_id = lookup.get(record.get("ticker"))
        rows.append(
            (
                instrument_id,
                record.get("return_date"),
                record.get("price_currency"),
                record.get("return_type"),
                float(record.get("return_value")),
                run_id,
            )
        )

    if not rows:
        return

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO portfolio.daily_returns (
                instrument_id, return_date, price_currency, return_type,
                return_value, calculation_run_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (
                instrument_id, return_date, price_currency, return_type, calculation_run_id
            )
            DO UPDATE SET
                return_value = EXCLUDED.return_value
            """,
            rows,
        )


def save_volatility_metrics(conn, volatility_df: pd.DataFrame, run_id: int) -> None:
    if volatility_df.empty:
        return

    required = {"ticker", "return_type", "metric_name", "metric_value", "window_days", "annualization_factor"}
    missing = sorted(required.difference(volatility_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for volatility_metrics: {missing}")

    lookup = resolve_instrument_ids(conn, volatility_df["ticker"].tolist())
    missing_tickers = sorted(set(volatility_df["ticker"]) - set(lookup))
    if missing_tickers:
        raise ValueError(f"Unknown instruments in volatility_metrics: {missing_tickers}")
    rows: list[tuple] = []

    for record in volatility_df.to_dict("records"):
        instrument_id = lookup.get(record.get("ticker"))
        rows.append(
            (
                run_id,
                instrument_id,
                record.get("return_type"),
                record.get("metric_name"),
                float(record.get("metric_value")),
                int(record.get("window_days")),
                int(record.get("annualization_factor")),
            )
        )

    if not rows:
        return

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO portfolio.volatility_metrics (
                calculation_run_id, instrument_id, return_type, metric_name,
                metric_value, window_days, annualization_factor
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (
                calculation_run_id, instrument_id, return_type, metric_name, window_days
            ) DO UPDATE SET
                metric_value = EXCLUDED.metric_value,
                annualization_factor = EXCLUDED.annualization_factor
            """,
            rows,
        )


def save_correlation_pairs(conn, correlation_df: pd.DataFrame, run_id: int) -> None:
    if correlation_df.empty:
        return

    required = {
        "ticker_a",
        "ticker_b",
        "return_type",
        "correlation_method",
        "window_days",
        "min_periods",
        "correlation_value",
    }
    missing = sorted(required.difference(correlation_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for correlation_pairs: {missing}")

    lookup = resolve_instrument_ids(conn, list(correlation_df["ticker_a"]) + list(correlation_df["ticker_b"]))
    missing_tickers = sorted(
        (set(correlation_df["ticker_a"]) | set(correlation_df["ticker_b"])) - set(lookup)
    )
    if missing_tickers:
        raise ValueError(f"Unknown instruments in correlation_pairs: {missing_tickers}")
    rows: list[tuple] = []

    for record in correlation_df.to_dict("records"):
        instrument_id_a = lookup.get(record.get("ticker_a"))
        instrument_id_b = lookup.get(record.get("ticker_b"))
        if instrument_id_a == instrument_id_b:
            raise ValueError(
                f"Correlation pair refers to the same instrument: {record.get('ticker_a')}"
            )
        if instrument_id_a > instrument_id_b:
            instrument_id_a, instrument_id_b = instrument_id_b, instrument_id_a
        rows.append(
            (
                run_id,
                record.get("return_type"),
                record.get("correlation_method"),
                instrument_id_a,
                instrument_id_b,
                int(record.get("window_days")),
                int(record.get("min_periods")),
                float(record.get("correlation_value")),
            )
        )

    if not rows:
        return

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO portfolio.correlation_pairs (
                calculation_run_id, return_type, correlation_method,
                instrument_id_a, instrument_id_b, window_days, min_periods,
                correlation_value
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (
                calculation_run_id, return_type, correlation_method,
                instrument_id_a, instrument_id_b, window_days
            ) DO UPDATE SET
                min_periods = EXCLUDED.min_periods,
                correlation_value = EXCLUDED.correlation_value
            """,
            rows,
        )


def correlation_matrix_to_pairs(
    matrix_df: pd.DataFrame,
    return_type: str,
    correlation_method: str,
    window_days: int,
    min_periods: int,
) -> pd.DataFrame:
    if matrix_df.empty:
        return pd.DataFrame(columns=[
            "ticker_a",
            "ticker_b",
            "return_type",
            "correlation_method",
            "window_days",
            "min_periods",
            "correlation_value",
        ])

    tickers = list(matrix_df.index)
    rows: list[dict] = []
    for i, left in enumerate(tickers):
        for right in tickers[i + 1 :]:
            value = float(matrix_df.loc[left, right])
            if pd.isna(value):
                continue
            rows.append(
                {
                    "ticker_a": left,
                    "ticker_b": right,
                    "return_type": return_type,
                    "correlation_method": correlation_method,
                    "window_days": window_days,
                    "min_periods": min_periods,
                    "correlation_value": value,
                }
            )

    return pd.DataFrame(rows)


def save_correlation_matrix_json(
    conn,
    matrix_df: pd.DataFrame,
    run_id: int,
    return_type: str,
    correlation_method: str,
    window_days: int,
) -> None:
    if matrix_df.empty:
        return

    payload = json.loads(matrix_df.to_json(orient="split"))
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO portfolio.correlation_matrices (
                calculation_run_id, return_type, correlation_method,
                window_days, matrix_json
            )
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (calculation_run_id, return_type, correlation_method, window_days)
            DO UPDATE SET
                matrix_json = EXCLUDED.matrix_json
            """,
            (run_id, return_type, correlation_method, window_days, json.dumps(payload)),
        )


def main() -> None:
    with get_connection() as conn:
        initialize_database(conn)
        inserted = seed_initial_instruments(conn, [STOXX_Global_Secelt_div_100_full, Portfolio])
        print(f"Seeded {inserted} instruments from initial dictionaries.")


if __name__ == "__main__":
    main()
