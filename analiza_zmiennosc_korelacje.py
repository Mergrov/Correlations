import yfinance as yf
import pandas as pd
import numpy as np
import os

from portfolio_db import (
    Portfolio as DB_PORTFOLIO,
    STOXX_Global_Secelt_div_100_full as DB_STOXX_INSTRUMENTS,
    correlation_matrix_to_pairs,
    create_calculation_run,
    ensure_data_source,
    get_connection,
    infer_listing,
    initialize_database,
    save_correlation_matrix_json,
    save_correlation_pairs,
    save_daily_prices,
    save_daily_returns,
    save_volatility_metrics,
    seed_initial_instruments,
)

STOXX_Global_Secelt_div_100_full = {
      #------STOXX financial sector of global select dividends-----
        "Legal and general": "LGEN.L",
        "Aegon": "AEG",
        "investec":"INVP.L",
        "ABN Amro" : "ABN.AS",
        "Natwest group": "NWG.L",
        "DBS group holdings": "D05.SI",
        "ASR NEDERLAND": "ASRNL.AS",
        "NN group": "NN.AS",
        "SUNCORP GROUP": "SUN.AX",
        "CREDIT AGRICOLE SA": "ACA.PA",
        "PRUDENTIAL FINANCIAL INC": "PRU",
        "POSTE ITALIANE":"PST.MI",
        "BNP PARIBAS SA":"BNP.PA",
        "HSBC HOLDINGS PLC":"HSBA.L",
        "ING GROEP":"INGA.AS",
        "T ROWE PRICE GROUP":"TROW",
        "AGEAS":"AGS.BR",
        "SCOR":"SCR.PA",
        "UNITED OVERSEAS BANK LTD":"U11.SI",
        "ALLIANZ":"ALV.DE",
        "AXA SA":"CS.PA",
        "BANK OF NOVA SCOTIA":"BNS.TO",
        "MANULIFE FINANCIAL":"MFC.TO",
        "SUN LIFE FINANCIAL INC":"SLF.TO",
        "POWER CORPORATION OF CANADA":"POW.TO",
        "ZURICH INSURANCE GROUP AG":"ZURN.SW",
        "DAIWA SECURITIES GROUP INC":"8601.T",
        "TRUIST FINANCIAL":"TFC",
        "US BANCORP":"USB",
        "BANK OF MONTREAL":"BMO.TO",
        "REGIONS FINANCIAL":"RF",
        "TORONTO DOMINION":"TD.TO",
        "PRINCIPAL FINANCIAL GROUP INC":"PFG",
        "NATIONAL AUSTRALIA BANK LTD":"NAB.AX",
        "HUNTINGTON BANCSHARES INC":"HBAN",
        "FIFTH THIRD BANCORP":"FITB",
        "CANADIAN IMPERIAL BANK OF COMMERCE":"CM.TO",
        "ROYAL BANK OF CANADA":"RY.TO",
        "CITIZENS FINANCIAL GROUP INC":"CFG",
        "FIDELITY NATIONAL FINANCIAL INC":"FNF",
        "NATIONAL BANK OF CANADA":"NA.TO",
    # -------- REST OF STOXX GLOBAL SELECT DIVIDEND 100 -------------------------
     "SITC INTERNATIONAL HOLDINGS LTD": "1308.HK",
      "TELEPERFORMANCE" : "TEP.PA",
     "B&M EUROPEAN VALUE RETAIL PLC" : "BME.L",
     "AKER BP" : "AKRBP.OL",
     "HP INC" : "HPQ",
     "TAYLOR WIMPEY PLC" : "TW.L",
     "WOODSIDE ENERGY GROUP LTD" : "WDS.AX",
     "SIGNIFY" : "LIGHT.AS",
     "BMW" : "BMW.DE",
     "KAWASAKI KISEN LTD" : "9107.T",
     "METCASH" : "MTS.AX",
     "SWIRE PACIFIC LTD A" : "SWRAY",
     "FORTESCUE LTD" : "FMG.AX",
     "ORLEN" : "PKN.WA",
     "PFIZER" : "PFE",
     "CLP HOLDINGS" : "0002.HK",
     "HONDA MOTOR" : "7267.T",
     "CAPITALAND INTEGRATED COMMERCIAL T" : "C38U.SI",
     "RUBIS" : "RUI.PA",
     "POWER ASSETS HOLDINGS" : "0006.HK",
     "HENDERSON LAND DEVELOPMENT LTD" : "0012.HK",
     "COVIVIO SA" : "COV.PA",
     "RIO TINTO LONDON" : "RIO.L",
     "JAPAN TOBACCO" : "2914.T",
     "WH GROUP" : "0288.HK",
     "HARVEY NORMAN HOLDINGS LTD" : "HVN.AX",
     "VERIZON COMMUNICATIONS INC" : "VZ",
     "RIO TINTO AUSTRALIA" : "RIO.AX",
     "TARGET CORP" : "TGT",
     "MITSUI FUDOSAN LOGISTICS PARK REIT" : "3471.T",
     "VOLKSWAGEN" : "VOW3.DE",
     "CK ASSET HOLDINGS LTD" : "1113.HK",
     "PHILLIPS 66" : "PSX",
     "GENERAL MILLS INC" : "GIS",
     "CONTACT ENERGY LTD" : "CEN.NZ",
     "JB HI-FI LTD" : "JBH.AX",
     "MAZDA MOTOR" : "7261.T",
     "MERCEDES-BENZ GROUP N AG" : "MBG.DE",
     "KOBE STEEL" : "5406.T",
     "JFE HOLDINGS" : "5411.T",
     "CHEVRON" : "CVX",
     "CAPITALAND ASCENDAS REIT" : "A17U.SI",
     "ORANGE SA" : "ORA.PA",
     "EDISON INTERNATIONAL" : "EIX",
     "XINYI GLASS HOLDINGS" : "0868.HK",
     "ROGERS COMMUNICATIONS" : "RCI-B.TO",
     "CONOCOPHILLIPS" : "COP",
     "COMCAST CLASS A" : "CMCSA",
     "SUN HUNG KAI PROPERTIES LTD" : "0016.HK",
     "CONSOLIDATED EDISON" : "ED",
     "AMGEN INC" : "AMGN",
     "DUKE ENERGY CORP" : "DUK",
     "DIAMONDBACK ENERGY" : "FANG",
     "SOUTHERN" : "SO",
     "INTERNATIONAL BUSINESS MACHINES" : "IBM",
     "DEVON ENERGY" : "DVN",
     "SEMPRA" : "SRE",
     "GILEAD SCIENCES" : "GILD",
     "ENTERGY CORP" : "ETR"
}

Portfolio = {

    "Cyber_Folks":"CBF.WA",
    "Games Workshop":"GAW.L",
    "XTB":"XTB.WA",
    "NWAI":"NWA.WA",
    "Scanway":"SCW.WA",
    "Hoya":"7741.T",
    "Kruk":"KRU.WA",
    "USD denominated em bonds":"VGEM.DE",
    "STOXX Global Select Dividends":"ISPA.DE",
    "Global water":"IH2O.L"
}

# --- KONFIGURACJA ---
tickers = {**STOXX_Global_Secelt_div_100_full, **Portfolio}

period = "5y"
output_dir = "Correlations"
os.makedirs(output_dir, exist_ok=True)

# --- POBIERANIE DANYCH ---
yf_tickers = list(tickers.values())
prices = yf.download(yf_tickers, period=period, progress=False, auto_adjust=False)

def extract_price_field(df, field, requested_tickers):
    if isinstance(df.columns, pd.MultiIndex):
        for level in range(df.columns.nlevels):
            if field in df.columns.get_level_values(level):
                result = df.xs(field, axis=1, level=level)
                if isinstance(result, pd.Series):
                    result = result.to_frame()
                return result
        return pd.DataFrame(index=df.index)
    if field not in df.columns:
        return pd.DataFrame(index=df.index)
    result = df[field]
    if isinstance(result, pd.Series):
        if len(requested_tickers) != 1:
            return pd.DataFrame(index=df.index)
        return result.to_frame(name=requested_tickers[0])
    return result


def extract_prices(df, requested_tickers):
    fields = {
        field: extract_price_field(df, field, requested_tickers)
        for field in ("Open", "High", "Low", "Close", "Adj Close", "Volume")
    }
    for frame in fields.values():
        if not frame.empty:
            frame.columns = [str(ticker) for ticker in frame.columns]
    close = fields["Adj Close"]
    if close.empty:
        close = fields["Close"]
    if close.empty:
        raise ValueError("Yahoo Finance returned no Close or Adj Close prices.")
    return fields, close


def prices_to_long(fields, requested_tickers):
    raw_close = fields["Close"]
    if raw_close.empty:
        raw_close = fields["Adj Close"]
    rows = []
    for ticker in requested_tickers:
        if ticker not in raw_close.columns:
            continue
        frame = pd.DataFrame(index=raw_close.index)
        for column, field in (
            ("open_price", "Open"),
            ("high_price", "High"),
            ("low_price", "Low"),
            ("close_price", "Close"),
            ("adjusted_close", "Adj Close"),
            ("volume", "Volume"),
        ):
            values = fields[field]
            frame[column] = values[ticker] if ticker in values.columns else np.nan
        frame = frame.dropna(subset=["close_price"])
        frame.index.name = "price_date"
        frame = frame.reset_index()
        frame["ticker"] = ticker
        frame["currency"] = infer_listing(ticker)[1]
        rows.append(frame)
    if not rows:
        raise ValueError("Yahoo Finance returned no daily prices for the requested instruments.")
    result = pd.concat(rows, ignore_index=True)
    return result.astype(object).where(pd.notna(result), None)


price_fields, close = extract_prices(prices, yf_tickers)

# usuwamy wiersze z brakującymi danymi (tylko wspólne daty)
close = close.dropna()
if close.empty:
    raise ValueError("Yahoo Finance returned no shared price dates for the requested instruments.")

# --- STOPY ZWROTU ---
rets = close.pct_change(fill_method=None).dropna()
if rets.empty:
    raise ValueError("At least two shared price dates are required to calculate returns.")

# --- ZMIENNOŚĆ ROCZNA ---
vol_annual = rets.std() * np.sqrt(252)

# --- KORELACJE ---
corr_matrix_pearson = rets.corr('pearson').round(4)
corr_matrix_spearman = rets.corr('spearman').round(4)
corr_combined = pd.concat(
    {
        "Pearson": corr_matrix_pearson,
        "Spearman": corr_matrix_spearman
    },
    axis=1
)

# --- TABELA Z WYNIKAMI ---
vol_df = pd.DataFrame({
    "Spolka": list(tickers.keys()),
    "Ticker_YF": [tickers[k] for k in tickers.keys()],
    "Volatility_roczna": [vol_annual[tickers[k]] for k in tickers.keys()]
})

# --- ZAPIS DO POSTGRESQL ---
price_currency_by_ticker = {ticker: infer_listing(ticker)[1] for ticker in yf_tickers}
price_long_df = prices_to_long(price_fields, yf_tickers)
return_frames = {
    "simple_local": rets,
    "log_local": np.log(close / close.shift(1)).dropna(),
}
return_rows = []
for return_type, frame in return_frames.items():
    long_returns = (
        frame.rename_axis(index="return_date", columns="ticker")
        .stack()
        .rename("return_value")
        .reset_index()
    )
    long_returns["price_currency"] = long_returns["ticker"].map(price_currency_by_ticker)
    long_returns["return_type"] = return_type
    return_rows.append(long_returns)
returns_long_df = pd.concat(return_rows, ignore_index=True)

window_days = int(len(rets))
volatility_rows = []
for ticker in rets.columns:
    daily_std = float(rets[ticker].std())
    volatility_rows.extend(
        [
            {
                "ticker": ticker,
                "return_type": "simple_local",
                "metric_name": "daily_std",
                "metric_value": daily_std,
                "window_days": window_days,
                "annualization_factor": 252,
            },
            {
                "ticker": ticker,
                "return_type": "simple_local",
                "metric_name": "annualized_volatility",
                "metric_value": daily_std * np.sqrt(252),
                "window_days": window_days,
                "annualization_factor": 252,
            },
        ]
    )
volatility_long_df = pd.DataFrame(volatility_rows)

# --- ZAPIS DO CSV ---
vol_df.to_csv(os.path.join(output_dir, "volatility.csv"), index=False)
corr_combined.to_csv(os.path.join(output_dir, "correlation_matrix.csv"), index=True)

min_periods = min(252, window_days)
correlation_matrices = {
    ("simple_local", "pearson"): rets.corr(method="pearson", min_periods=min_periods),
    ("simple_local", "spearman"): rets.corr(method="spearman", min_periods=min_periods),
}
correlation_pairs = pd.concat(
    [
        correlation_matrix_to_pairs(
            matrix, return_type, method, window_days, min_periods
        )
        for (return_type, method), matrix in correlation_matrices.items()
    ],
    ignore_index=True,
)

with get_connection() as conn:
    initialize_database(conn)
    seed_initial_instruments(conn, [DB_STOXX_INSTRUMENTS, DB_PORTFOLIO])
    data_source_id = ensure_data_source(
        conn, "Yahoo Finance", "https://finance.yahoo.com"
    )
    run_id = create_calculation_run(
        conn,
        run_name=f"Yahoo Finance {period}",
        data_source_id=data_source_id,
        price_currency="LOCAL",
        period_start=close.index.min().date().isoformat(),
        period_end=close.index.max().date().isoformat(),
        return_frequency="daily",
        annualization_factor=252,
        min_periods=min_periods,
        script_version="1",
    )
    save_daily_prices(conn, price_long_df, data_source_id)
    save_daily_returns(conn, returns_long_df, run_id)
    save_volatility_metrics(conn, volatility_long_df, run_id)
    for (return_type, method), matrix in correlation_matrices.items():
        method_pairs = correlation_pairs[
            (correlation_pairs["return_type"] == return_type)
            & (correlation_pairs["correlation_method"] == method)
        ]
        save_correlation_pairs(conn, method_pairs, run_id)
        save_correlation_matrix_json(
            conn, matrix, run_id, return_type, method, window_days
        )

print("Tabela zmienności:")
print(vol_df.to_string(index=False))
print("\nMacierz korelacji:")
print(corr_combined.round(4))
print(f"\nPostgreSQL: zapisano przebieg obliczeń run_id={run_id}.")