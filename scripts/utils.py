from itertools import combinations


def overall_mean(iterable):
    total_sum = 0
    count = 0
    i = 0
    for value in iterable:
        i += 1
        total_sum += float(value)
        count += 1
    return total_sum / count if count else None


def overall_median(iterable):
    values = sorted(iterable)
    n = len(values)
    i = 0

    if n == 0:
        return None
    if n % 2 == 1:
        return values[n//2]
    else:
        return (values[n//2 - 1] + values[n//2]) / 2.0
    

def unique_pairs(strings):
    return list(combinations(set(strings), 2))
