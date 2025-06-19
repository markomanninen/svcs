def old_style_function(items):
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
    return result
