from gpt_request import ChatGLMAPI
from gpt_request import QwenturboAPI
from gpt_request import ERNIEAPI
from gpt_request import OllamaAPI
from prompt_template import *

import random  
import string  
import datetime
import time
from blogs import Article
from comments import Comment
# from thread_person import Person
from thread_person1 import Person
from thread_timer import Clock
import copy
from weiboSimulator import Weibo
from datetime import datetime
import json
import threading
from weiboSimulator import Weibo

if __name__ == '__main__':
    ##
    probs = [0.5, 0.6, 0.5, 0.2, 0.8, 0.5, 0.4, 0.8]

    chatglm_api = ChatGLMAPI() #GLM3-6B
    # qwen_api = QwenturboAPI() #Qwen-turbo
    qwen_api = OllamaAPI() #Qwen1.5:0.5b(ollama)
    ernie_api = ERNIEAPI() #ERNIE4.0(文心)


    # 读取 user_category.json 文件
    with open('DATASET_USERS/core+common_profile(20,0).json', 'r') as f:
        user_categories = json.load(f)

    # 创建一个字典来映射 id 到 api
    id_to_api = {item['user_id']: item['api'] for item in user_categories}
    # 将 API 名称映射到具体的 API 实例
    api_name_to_instance = {
        'chatglm_api': chatglm_api,
        'qwen_api': qwen_api,
        'ernie_api': ernie_api
    }

    remote_api = Weibo()
    sim_time = 10000

    users = []
    apis = []
    profiles = []
    category = []
    for user_info in user_categories:
        user_id = user_info['user_id']
        api_name = user_info['api']
        user_profile = user_info['profile']
        # 根据 user_category.json 中的信息获取 API
        if api_name not in api_name_to_instance:
            raise ValueError("don't know api")  # 如果找不到对应的 API，则报错
        user = user_id
        print(user)
        users.append(user)
        apis.append(api_name_to_instance[api_name])
        if api_name == "qwen_api": # common user
            category.append(0)
        else: 
            category.append(1) #core user
        profiles.append(user_profile)

    print(users)
    probs = [random.uniform(0.0, 1.0) for _ in range(len(users))]
    users = [Person(users[i], profiles[i], probs[i], sim_time, apis[i], remote_api, category[i]) for i in range(len(users))]
    print()
    # 粉丝关系配置
    # 读取关系网络数据集并建立 follow 关系
    with open('DATASET_USERS/relationship_network(20,0).json', 'r') as f:
        relationship_data = json.load(f)
    user_dicts = {str(user.name): user for user in users}

    for relationship in relationship_data:
        retweet_user_id = str(relationship['retweet_user_id'])
        original_user_id = str(relationship['original_user_id'])
        if retweet_user_id in user_dicts and original_user_id in user_dicts:
            user_dicts[retweet_user_id].follow(user_dicts[original_user_id].user_id)
            # follow(retweet_user_id , original_user_id)
        else:
            print(f"User ID {retweet_user_id} or {original_user_id} not found in users.")

    print(f"According to People's Daily, Tokyo, June 27 (Xu Ke, Chen Jianjun) – On June 24 local time, Shinsuke Yamanaka, the chairman of the Japanese Nuclear Regulation Authority, inspected the nuclear wastewater discharge equipment and other facilities at Tokyo Electric Power Company's Fukushima Daiichi Nuclear Power Station. He announced that the Nuclear Regulation Authority will begin pre-use inspections of the marine discharge equipment from June 28. The Japanese government's plan to discharge Fukushima Daiichi's radioactive nuclear wastewater into the sea this summer has faced strong global criticism and opposition, and continues to be opposed domestically across various sectors.")  # offline news
    user_dicts["1111111111"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["6993823294"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["5393135816"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["1643971635"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["6317134281"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["1455153401"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["1553177803"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["5230132970"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["1795548274"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")
    user_dicts["5333693607"].post_weibo("The chairman of Japan's Nuclear Regulation Authority inspected Fukushima's nuclear wastewater facilities, sparking global and domestic outrage over plans to discharge radioactive water this summer.")

    # 创建一个共享的 Condition 对象
    shared_condition = threading.Condition()

    for user in users:
        user.clock = shared_condition
        user.start()
    clock_process = Clock(update_interval=300, time_step=60, condition=shared_condition)  # condition
    clock_process.start()
    while True:
        user_info = {}
        for user in users:
            tmp = {"name": user.name}
            user_info[user.user_id] = tmp
        with open("user_info.json", "w") as outfile:
            json.dump(user_info, outfile)
        time.sleep(5)

    for user in users:
        user.join()
    thread_static.join()

