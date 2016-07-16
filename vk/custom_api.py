from .vkapi import VkApi


class PublicApiCommands:
    def __init__(self, access_token, v, domen):
        self.connection = VkApi(access_token, v)
        self.domen = domen

    def get_post_list(self, count):
        method = "wall.get"
        params = "owner_id=-%s" % self.domen
        items = self.connection.complex_request(method, params, count)
        return items

    def get_comments_form_post(self, post):
        method = "wall.getComments"
        params = "owner_id=-%s&need_likes=1" % self.domen
        post_id = post["id"]
        parameters_with_post_id = params + "&post_id=%s" % post_id
        items = self.connection.complex_request(method, parameters_with_post_id)
        return items

    def get_comments_from_post_list(self, post_list):
        result_list_of_items = []
        for post in post_list:
            items = self.get_comments_form_post(post)
            result_list_of_items.extend(items)
        return result_list_of_items
