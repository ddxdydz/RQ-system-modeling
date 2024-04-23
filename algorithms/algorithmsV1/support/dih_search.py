def dih_search(value, left: int, right: int, key):
    average = (left + right) // 2
    if key(average) == value:
        return average
    elif right - left == 1:
        if key(left) < value <= key(right):
            return right
        elif key(left) == value:
            return left
        elif key(right) < value:
            return right + 1
        elif key(left) > value:
            return left
    elif left == right:
        if value <= key(left):
            return left
        return right + 1
    else:
        if key(average) < value:
            return dih_search(value, average, right, key=key)
        return dih_search(value, left, average, key=key)
