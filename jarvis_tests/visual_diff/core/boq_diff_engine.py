def compare_boq(old, new):
    diff = {
        "missing": [],
        "added": [],
        "modified": [],
        "quantity_changes": []
    }

    old_map = {i["id"]: i for i in old}
    new_map = {i["id"]: i for i in new}

    # Missing items
    for id in old_map:
        if id not in new_map:
            diff["missing"].append(old_map[id])

    # Added items
    for id in new_map:
        if id not in old_map:
            diff["added"].append(new_map[id])

    # Modified items
    for id in old_map:
        if id in new_map:
            if old_map[id]["qty"] != new_map[id]["qty"]:
                diff["quantity_changes"].append({
                    "id": id,
                    "old": old_map[id]["qty"],
                    "new": new_map[id]["qty"]
                })

    return diff