# encoding=utf-8
import random

from libs.user_agents import agents


class UserAgentMiddleware(object):
    """ Randomly choose a User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

