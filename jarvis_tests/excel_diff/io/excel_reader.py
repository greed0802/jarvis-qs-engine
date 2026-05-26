import pandas as pd

def load_boq(file_path):
    df = pd.read_excel(file_path)

    df = df.fillna("")

    # normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    return df
