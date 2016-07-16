import requests
import json
import math
import time

from .exceptions import VkApiError

MAX_PER_REQ = {
    "wall.get": 100,
    "groups.getById": 500,
    "wall.getComments": 100,
}


class VkApi:
    def __init__(self, access_token, v):
        self.access_token = access_token
        self.v = v

    def request(self, method, parameters):
        url = "https://api.vk.com/method/%s?%s&access_token=%s&v=%s"
        response = requests.get(url % (method, parameters, self.access_token, self.v))
        return json.loads(response.text)

    @classmethod
    def extract_response(cls, response):
        if "response" in response:
            if "items" in response["response"]:
                count, items = cls._extract_response_itemstype(response)
            else:
                count, items = cls._extract_response_non_itemstype(response)
        else:
            code, message = cls._extract_response_error(response)
            raise VkApiError(code, message)
        return (count, items)

    @classmethod
    def _extract_response_itemstype(cls, response):
        count = response["response"]["count"]
        items = response["response"]["items"]
        return (count, items)

    @classmethod
    def _extract_response_non_itemstype(cls, response):
        count = len(response["response"])
        items = response["response"]
        return (count, items)

    @classmethod
    def _extract_response_error(cls, response):
        code = response["error"]["error_code"]
        message = response["error"]["error_msg"]
        return (code, message)

    def complex_request(self, method, parameters,
                        desired_count_of_items=None, max_items_per_request=None):
        result_list_of_items = []
        if not desired_count_of_items:
            desired_count_of_items = self.get_count(method, parameters)
        if not max_items_per_request:
            max_items_per_request = MAX_PER_REQ[method]
        parameters += "&count=%s" % desired_count_of_items
        for i in range(math.ceil(desired_count_of_items / max_items_per_request)):
            offset = str(i * max_items_per_request)
            parameters_with_offset = parameters + "&offset=%s" % offset
            response = self.request(method, parameters_with_offset)
            count, items = self.extract_response(response)
            result_list_of_items.extend(items)

            time.sleep(0.334)
        return result_list_of_items

    def get_count(self, method, parameters):
        response = self.request(method, parameters)
        count, items = self.extract_response(response)
        return count
