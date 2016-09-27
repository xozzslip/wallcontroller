# {
#   "100": [{"likes_c": 0, "pk": 28, "sync_ts": "2016-09-27 10:13:07.933107+00:00"},
#   {"likes_c": 0, "pk": 61, "sync_ts": "2016-09-27 10:13:08.905418+00:00"}],
#   "4": [{"likes_c": 0, "pk": 3, "sync_ts": "2016-09-27 10:13:07.923804+00:00"},
#   {"likes_c": 0, "pk": 36, "sync_ts": "2016-09-27 10:13:08.896853+00:00"}]
# }

LOYALTY_COEF = 0.5
ZERO_LIKES_PERIOD = 0.2


def to_dict(qs):
    comments_dict = {comment.vk_id: [] for comment in qs}
    for comment in qs:
        comment_info = {
            "sync_ts": comment.sync_ts,
            "likes_c": comment.likes_count,
            "pk": comment.pk
        }
        comments_dict[comment.vk_id].append(comment_info)
    return comments_dict


def deleting_comments_list(comments_dict):
    avarage_likes_c = calc_avarage(comments_dict)
    deleting_comments_list = []
    for vk_id, comment in comments_dict.items():
        lifetime = (comment[-1]["sync_ts"] - comment[0]["sync_ts"]).seconds / 3600
        likes_c = comment[-1]["likes_c"]
        normalized_likes_c = (likes_c / avarage_likes_c) * LOYALTY_COEF
        if not is_comment_good(normalized_likes_c, lifetime):
            deleting_comments_list.append(vk_id)
    return deleting_comments_list


def is_comment_good(normalized_likes_c, lifetime):
    return normalized_likes_c >= likes_function(lifetime)


def calc_avarage(comments_dict):
    count_of_timed_comments = 0
    sum_of_likes_count = 0
    for timed_comments in comments_dict.values():
        for stamp in timed_comments:
            sum_of_likes_count += stamp["likes_c"]
            count_of_timed_comments += 1
    if sum_of_likes_count == 0:
        sum_of_likes_count = 1
    return sum_of_likes_count / count_of_timed_comments


def likes_function(t):
    required_likes_c = (t ** 4 - ZERO_LIKES_PERIOD * t ** 3) / (t ** 4 + t ** 2 + 0.001)
    return required_likes_c
