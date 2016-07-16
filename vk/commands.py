from .vkapi import VkApi

connection = VkApi(access_token="", v="5.52")


def get_group_domen(domen_name):
    method = "groups.getById"
    params = "group_id=%s" % domen_name
    items = connection.complex_request(method, params)
    group = items[0]
    return group["id"]
