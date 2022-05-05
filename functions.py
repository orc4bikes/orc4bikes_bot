from datetime import timedelta

def to_readable_td(diff: timedelta):
    d = diff.days
    h = diff.seconds // 3600
    m = (diff.seconds % 3600) // 60
    s = (diff.seconds % 3600) % 60
    if diff.days:
        output = f"{d} days, {h} hours, {m} minutes and {s} seconds."
    else:
        output = f"{h} hours, {m} minutes and {s} seconds."
    return output
