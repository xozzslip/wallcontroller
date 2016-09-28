LOYALTY_COEF = 1
ZERO_LIKES_PERIOD = 0.2


def deleting_comments_list(comments_list):
    deleting_comments_list = []
    avarage_likes_c = calc_avarage(comments_list)
    for comment in comments_list:
        lifetime = (comment.sync_ts - comment.creation_ts) / 3600
        likes_c = comment.likes_count
        normalized_likes_c = (likes_c / (avarage_likes_c * LOYALTY_COEF))
        if not is_comment_good(normalized_likes_c, lifetime):
            deleting_comments_list.append(comment)
    return deleting_comments_list


def is_comment_good(normalized_likes_c, lifetime):
    return normalized_likes_c >= likes_function(lifetime)


def calc_avarage(comments_list):
    if not comments_list:
        return 0
    return sum([c.likes_count for c in comments_list]) / len(comments_list)


def likes_function(t):
    required_likes_c = (t ** 4 - ZERO_LIKES_PERIOD * t ** 3) / (t ** 4 + t ** 2 + 0.001)
    return required_likes_c
