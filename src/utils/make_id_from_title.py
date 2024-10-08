def make_id_from_title(title):
    title = title.replace("§", "section")
    return "".join(
        char.lower() for char in title if char.isalnum() or char == " "
    ).replace(" ", "_")