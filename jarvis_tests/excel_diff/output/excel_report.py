import pandas as pd

def export_diff(diff, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        pd.DataFrame(diff["missing"]).to_excel(writer, sheet_name="Missing", index=False)
        pd.DataFrame(diff["added"]).to_excel(writer, sheet_name="Added", index=False)
        pd.DataFrame(diff["quantity_changes"]).to_excel(writer, sheet_name="Qty Changes", index=False)
        pd.DataFrame(diff["description_changes"]).to_excel(writer, sheet_name="Desc Changes", index=False)