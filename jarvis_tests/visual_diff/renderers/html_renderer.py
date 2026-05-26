def render_html(diff):
    html = "<h1>BOQ VISUAL DIFF REPORT</h1>"

    html += "<h2>Missing Items</h2>"
    for item in diff["missing"]:
        html += f"<div style='color:red'>{item}</div>"

    html += "<h2>Added Items</h2>"
    for item in diff["added"]:
        html += f"<div style='color:green'>{item}</div>"

    html += "<h2>Quantity Changes</h2>"
    for item in diff["quantity_changes"]:
        html += f"<div>{item['id']}: {item['old']} → {item['new']}</div>"

    return html