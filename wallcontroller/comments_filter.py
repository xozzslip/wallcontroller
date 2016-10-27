ZERO_PERIOD_IN_SECOND = 15 * 60
LOYAL_PERIOD_IN_SECOND = 5 * (60 * 60)


def likes_function(t, end_count):
    if t < ZERO_PERIOD_IN_SECOND:
        return 0
    elif t > LOYAL_PERIOD_IN_SECOND:
        return end_count
    else:
        return round(t * end_count / (LOYAL_PERIOD_IN_SECOND - ZERO_PERIOD_IN_SECOND))


def find_trash_comments(comments_list, end_count=1):
    deleting_comments_list = []
    for comment in comments_list:
        lifetime = comment.sync_ts - comment.creation_ts
        if comment.likes_count < likes_function(lifetime, end_count):
            deleting_comments_list.append(comment)
    return deleting_comments_list
