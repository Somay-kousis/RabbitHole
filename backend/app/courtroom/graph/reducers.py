def merge_perspectives(left, right):
    if not left:
        return right or []

    if not right:
        return left

    merged = {perspective["id"]: perspective for perspective in left}

    for perspective in right:
        existing = merged.get(perspective["id"], {})
        merged[perspective["id"]] = {
            **existing,
            **perspective,
        }

    return sorted(merged.values(), key=lambda perspective: perspective["id"])
