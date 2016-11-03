def likes_function(t, end_count, end_time, loyal_time):
    if t < loyal_time:
        return 0
    elif t > end_time:
        return end_count
    else:
        return round(t * end_count / (end_time - loyal_time))
