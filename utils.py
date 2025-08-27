from translations import translations

def generate_markdown_table(rows, cols, current_language):
    if rows <= 0 or cols <= 0:
        return ""
    
    header_row = "| " + " | ".join([translations[current_language]["table_header"].format(i+1) for i in range(cols)]) + " |\n"
    separator_row = "| " + " | ".join(["-" * 10 for _ in range(cols)]) + " |\n"

    data_rows = []
    for r in range(rows):
        row_content = "| " + " | ".join([translations[current_language]["table_cell"].format(r+1, c+1) for c in range(cols)]) + " |"
        data_rows.append(row_content)

    return header_row + separator_row + "\n".join(data_rows) + "\n"
