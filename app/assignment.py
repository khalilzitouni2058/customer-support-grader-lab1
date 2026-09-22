def assigned_annotators(item_id: int) -> list[str]:
    """Return the two annotator IDs assigned to an item.

    Balanced design for 150 items:
      1-25   -> A,B
      26-50  -> A,C
      51-75  -> A,D
      76-100 -> B,C
      101-125-> B,D
      126-150-> C,D
    """
    if 1 <= item_id <= 25:
        return ["A", "B"]
    if 26 <= item_id <= 50:
        return ["A", "C"]
    if 51 <= item_id <= 75:
        return ["A", "D"]
    if 76 <= item_id <= 100:
        return ["B", "C"]
    if 101 <= item_id <= 125:
        return ["B", "D"]
    if 126 <= item_id <= 150:
        return ["C", "D"]
    return []
