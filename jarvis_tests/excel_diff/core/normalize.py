def normalize_boq(df):
    required_cols = ["item", "description", "qty", "unit"]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    return df[required_cols]