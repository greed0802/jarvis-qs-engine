def compare_boq(old_df, new_df):
    old_map = old_df.set_index("item").to_dict("index")
    new_map = new_df.set_index("item").to_dict("index")

    diff = {
        "missing": [],
        "added": [],
        "quantity_changes": [],
        "description_changes": []
    }

    # missing
    for item in old_map:
        if item not in new_map:
            diff["missing"].append(old_map[item])

    # added
    for item in new_map:
        if item not in old_map:
            diff["added"].append(new_map[item])

    # modified
    for item in old_map:
        if item in new_map:
            old_row = old_map[item]
            new_row = new_map[item]

            if old_row["qty"] != new_row["qty"]:
                diff["quantity_changes"].append({
                    "item": item,
                    "old": old_row["qty"],
                    "new": new_row["qty"]
                })

            if old_row["description"] != new_row["description"]:
                diff["description_changes"].append({
                    "item": item,
                    "old": old_row["description"],
                    "new": new_row["description"]
                })

    return diff