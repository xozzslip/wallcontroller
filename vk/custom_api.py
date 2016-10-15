import math
import time
from functools import reduce
from .vkapi import VkApi, SLEEP

REQ_LIMIT_IN_EXECUTE = 25


class PublicApiCommands:
    def __init__(self, access_token, domen):
        self.connection = VkApi(access_token)
        self.domen = domen
        self.executable_commands = ExecutablePublicApiCommands(access_token, domen)

    def get_post_list(self, count):
        method = "wall.get"
        params = "owner_id=-%s" % self.domen
        items = self.connection.make_request(method, params, count)
        return items

    def get_comments_form_post(self, post_id):
        method = "wall.getComments"
        params = "owner_id=-%s&need_likes=1" % self.domen
        parameters_with_post_id = params + "&post_id=%s" % post_id
        items = self.connection.make_request(method, parameters_with_post_id)
        return items

    def get_comments_from_post_list(self, post_list):
        return self.executable_commands.get_comments_from_post_list(post_list)

    def get_comments_from_post_list_not_exe(self, post_list):
        result_list_of_items = []
        for post in post_list:
            items = self.get_comments_form_post(post["id"])
            result_list_of_items.extend(items)
        return result_list_of_items

    def create_post(self, text):
        method = "wall.post"
        params = "owner_id=-%s&from_group=1&message=%s" % (self.domen, text)
        post_id = self.connection.make_request(method, params)[0]
        return post_id

    def delete_post(self, post_id):
        method = "wall.delete"
        params = "owner_id=-%s&post_id=%s" % (self.domen, post_id)
        self.connection.make_request(method, params)

    def create_comment(self, text, post_id):
        method = "wall.createComment"
        params = "owner_id=-%s&post_id=%s&message=%s" % (self.domen, post_id, text)
        comment_id = self.connection.make_request(method, params)["comment_id"]
        return comment_id

    def delete_comments(self, comments_list):
        return self.executable_commands.delete_comments_from_comments_list(comments_list)

    def delete_comment(self, comment_id):
        method = "wall.deleteComment"
        params = "owner_id=-%s&comment_id=%s" % (self.domen, comment_id)
        self.connection.make_request(method, params)

    def get_post_by_text(self, text):
        CHECKING_COUNT = 100
        post_list = self.get_post_list(count=CHECKING_COUNT)
        desired_post = [post for post in post_list if text in post["text"]][0]
        return desired_post

    def get_groups_under_moderation(self):
        method = "groups.get"
        params = "filter=admin,editor,moder&count=1000"
        return self.connection.make_request(method, params)


class ExecutablePublicApiCommands:
    def __init__(self, access_token, domen):
        self.connection = VkApi(access_token)
        self.domen = domen

    @staticmethod
    def split_posts(post_list):
        lim = REQ_LIMIT_IN_EXECUTE
        range_ = math.ceil(len(post_list) / REQ_LIMIT_IN_EXECUTE)
        return [post_list[i * lim: (i + 1) * lim] for i in range(range_)]

    def responses_list_to_comments(self, responses_list):
        responses_list = self.adding_post_id_to_response_list(responses_list)
        list_of_items = [post_comments["items"] for post_comments in responses_list]
        return reduce(lambda res, x: res + x, list_of_items, [])

    def adding_post_id_to_response_list(self, responses_list):
        for response in responses_list:
            for item in response["items"]:
                item.update({"post_id": response["post_id"]})
        return responses_list

    def get_chunck_of_comments_form_post_list(self, limited_post_list):
        method = "execute"
        post_ids_list = [post["id"] for post in limited_post_list]
        сode = """
            var post_list = %s;
            var comments_list = [];
            while (post_list.length > 0){
                var current_post = post_list.pop();
                var comments = API.wall.getComments({
                    "owner_id": -%s,
                    "need_likes": 1,
                    "post_id": current_post,
                    "count": 100,
                });
                comments.post_id = current_post;
                comments_list.push(comments);
            }
            return comments_list;
        """ % (post_ids_list, self.domen)
        params = "code=%s" % сode
        responses_list = self.connection.make_request(method, params)
        return self.responses_list_to_comments(responses_list)

    def delete_chunck_of_comments_from_comments_list(self, limited_comments_list):
        method = "execute"
        comments_ids_list = [comment["id"] for comment in limited_comments_list]
        сode = """
            var comments_list = %s;
            var responses = [];
            while (comments_list.length > 0){
                var current_comment = comments_list.pop();
                var current_response = API.wall.deleteComment({
                    "owner_id": -%s,
                    "comment_id": current_comment,
                });
                responses.push(current_response);
            }
            return responses;
        """ % (comments_ids_list, self.domen)
        params = "code=%s" % сode
        responses_list = self.connection.make_request(method, params)
        return responses_list

    def get_comments_from_post_list(self, post_list):
        items = []
        for limited_post_list in self.split_posts(post_list):
            items += self.get_chunck_of_comments_form_post_list(limited_post_list)
        return items

    def delete_comments_from_comments_list(self, comments_list):
        items = []
        for limited_comments_list in self.split_posts(comments_list):
            items += self.delete_chunck_of_comments_from_comments_list(limited_comments_list)
        return items
