def compare_maps(old_map, new_map):
    diff = {
        "missing": [],
        "added": [],
        "qty_changes": [],
        "desc_changes": []
    }

    for item in old_map:
        if item not in new_map:
            diff["missing"].append(item)

    for item in new_map:
        if item not in old_map:
            diff["added"].append(item)

    for item in old_map:
        if item in new_map:
            if old_map[item]["qty"] != new_map[item]["qty"]:
                diff["qty_changes"].append(item)

            if old_map[item]["description"] != new_map[item]["description"]:
                diff["desc_changes"].append(item)

    return diff