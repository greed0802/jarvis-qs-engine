def compare_boQ_outputs(new_output, golden_output):
    diffs = []

    if new_output.total_items != golden_output.total_items:
        diffs.append("ITEM COUNT MISMATCH")

    if new_output.total_quantity != golden_output.total_quantity:
        diffs.append("QUANTITY MISMATCH")

    if new_output.level_structure != golden_output.level_structure:
        diffs.append("LEVEL STRUCTURE CHANGED")

    if new_output.missing_items:
        diffs.append("MISSING ITEMS DETECTED")

    if new_output.extra_items:
        diffs.append("EXTRA ITEMS DETECTED")

    return diffs