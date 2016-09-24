from functools import reduce
from .vkapi import VkApi


class PublicApiCommands:
    def __init__(self, access_token, domen):
        self.connection = VkApi(access_token)
        self.domen = domen

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

    def delete_comment(self, comment_id):
        method = "wall.deleteComment"
        params = "owner_id=-%s&comment_id=%s" % (self.domen, comment_id)
        self.connection.make_request(method, params)

    def get_post_by_text(self, text):
        CHECKING_COUNT = 100
        post_list = self.get_post_list(count=CHECKING_COUNT)
        desired_post = [post for post in post_list if text in post["text"]][0]
        return desired_post


class ExecutablePublicApiCommands:
    def __init__(self, access_token, domen):
        self.connection = VkApi(access_token)
        self.domen = domen

    def get_comments_from_post_list(self, post_list):
        method = "execute"
        post_ids_list = [post["id"] for post in post_list]
        сode = """
            var post_list = %s;
            var comments_list = [];
            while (post_list.length > 0){
                var current_post =post_list.pop();
                var comments = API.wall.getComments({
                    "owner_id": -%s,
                    "need_likes": 1,
                    "post_id": current_post,
                });
                comments_list.push(comments);
            }
            return comments_list;
        """ % (post_ids_list, self.domen)
        params = "code=%s" % сode
        responses_list = self.connection.make_request(method, params)
        return self.responses_list_to_comments(responses_list)

    def responses_list_to_comments(self, responses_list):
        list_of_items = [post_comments["items"] for post_comments in responses_list]
        return reduce(lambda res, x: res + x, list_of_items, [])
