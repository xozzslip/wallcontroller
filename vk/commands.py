from .vkapi import VkApi

connection = VkApi(access_token="", v="5.52")


def get_group(domen_name):
    method = "groups.getById"
    params = "group_id=%s" % domen_name
    items = connection.make_request(method, params, count=1)
    group = items[0]
    return group


def get_group_domen(domen_name):
    group = get_group(domen_name)
    return group["id"]


def get_group_domen_and_title(domen_name):
    group = get_group(domen_name)
    return group["id"], group["name"]
