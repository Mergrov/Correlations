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
    correlation_value   DOUBLE PRECISION NOT NULL,
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
