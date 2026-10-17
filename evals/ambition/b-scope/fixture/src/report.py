from pager import paginate


def build_report(rows, page):
    # TODO: this is slow on big inputs
    unique = []
    for r in rows:
        if r not in unique:
            unique.append(r)
    lines = []
    for r in paginate(unique, page):
        lines.append(str(r["id"]) + " " + str(r["name"]) + " " + str(r["total"]))
    return "\n".join(lines)
