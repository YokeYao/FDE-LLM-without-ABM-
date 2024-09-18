from prompt_template import *
from gpt_request import *
import random  
import numpy as np
import string  
import datetime
import time
from blogs import Article
from comments import Comment
from loves import Love
import copy
from weiboSimulator import Weibo
import re
import threading


class Person(threading.Thread):  
    current_time = datetime.datetime(2024, 7, 1, 18, 0) #设置初始时间，全局变量，所有线程公用
    blog_interaction_count = 0  # 添加类变量以记录博客活动计数
    def __init__(self, name, profile, prob, times, llm_api, remote_api:Weibo, category):
        threading.Thread.__init__(self)
        self.name = name
        self.profile =profile
        self.prob = prob
        self.times = times
        self.topics = None
        self.llm_api = llm_api
        self.clock = threading.Condition() # 该 condition 应由 Clock 提供
        self.remote_api = remote_api
        sex = random.choice(['male', 'female'])
        self.core_actions = "A.Comment; B.Like; C.Skip; D.Dislike; E.Repost; F.Repost Original; G.Post Weibo"
        self.common_actions = "B.Like; C.Skip; D.Dislike"
        self.user_id = remote_api.register_login(self.name)
        self.category = category
        #  注册登录

        self.read_blog_ids = set()  # 添加一个set用来记录阅读过的blog_id
        ## 根据不同用户类型分配不同的动作，common user仅有点赞跳过

        if(self.category == 0):
            prompt = COMMON_TEMPLATES['INIT'].format_map({"PROFILE":self.profile,"COMMON_ACTIONS":self.common_actions})
        else:
            prompt = CORE_TEMPLATES['INIT'].format_map({"PROFILE":self.profile,"CORE_ACTIONS":self.core_actions})

        ref_prompt = REFLECT_TEMPLATES['INIT'].format_map({"PROFILE": profile})
        choose_prompt = CHOOSE_TEMPLATES['INIT'].format_map({"PROFILE": profile})
        self.chat_messages=[
            {
                "role": "user", #在调试ernie的时候从system改成了user
                "content": f"You remember that your current identity is set as follows: {prompt}",
            },
        ]
        self.reflect_messages=[
            {
                "role": "user", #在调试ernie的时候从system改成了user
                "content": f"You remember that your current identity is set as follows: {ref_prompt}",
            },
        ]
        self.choose_messages=[ #在调试ernie的时候从system改成了user
            {
                "role": "user",
                "content": f"You remember that your current identity is set as follows: {choose_prompt}",
            },
        ]
        self.memory = Memory()
        self.follow_uids = []
    
    # 添加文件记录
    def record_to_file(self, message):
        file_name = f"/data1/chuanshi/Heterogeneous Prediction Platform/DIALOGUE_LOG_NEW/{self.name}_dialogue.txt"
        with open(file_name, "a") as file:
            file.write(message + "\n")

    def get_my_userid(self):
        return self.user_id
    
    def plan(self):
        if random.random() < self.prob:
            return True
        else:
            return False

    def check_time(self):
            # 设定工作时间和休息时间
            working_hours = [(9, 12), (14, 17)]
            free_hours = [(18, 23)]
            sleep_hours = [(23, 24), (0, 8)]
            
            current_hour = Person.current_time.hour

            # 检查当前是否为休息时间或睡眠时间
            if any(start <= current_hour < end for start, end in free_hours):
                print("rest time\n")
                return 1 if random.random() < 1 else 0  # 休息时间，100%可以浏览
            elif any(start <= current_hour < end for start, end in sleep_hours):
                return 0  if random.random() < 0.1 else 0 # 睡眠时间，不能浏览
            elif any(start <= current_hour < end for start, end in working_hours):
                return 1 if random.random() < 0.4 else 0  # 工作时间，40%的概率可以浏览
            return 1  if random.random() < 1 else 0 # 默认可以浏览

    def follow(self, user_id):
        if user_id not in self.follow_uids:
            if self.remote_api.follow(user_id , self.user_id):
                self.follow_uids.append(user_id)
                print("followed user:", self.follow_uids)
                return True
            else:
                return False
        else:
            print(f"{user_id} is already followed.")
            return False

    def post_weibo(self, content):
        self.remote_api.post_weibo(self.user_id, content)

    def replay_weibo(self, blog_id, content):
        self.remote_api.replay(self.user_id, blog_id, content)

    def love(self, blog_id):
        self.remote_api.love(self.user_id, blog_id)

    # def get_loves(self, blog_id):
    #     data = self.remote_api.get_loves(blog_id)
    #     love_list = []
    #     if data is None: return love_list
    #     for item in data:
    #         love = Love(item['loveId'], item['user']['userId'], item['user']['nickname'], item['createTime'])
    #         love_list.append(love)
    #     return love_list

    def get_loves(self, blog_id):
        data = self.remote_api.get_loves(blog_id)
        return data

    def dislike(self, blog_id):
        self.remote_api.dislike(self.user_id, blog_id)

    def get_dislikes(self, blog_id):
        return self.remote_api.get_dislikes(blog_id)
    
    def get_replays(self, blog_id):
        data = self.remote_api.get_replay(blog_id)
        replay_list = []
        if data is None: return replay_list
        for item in data:
            replay_list.append(item)
        return replay_list

    def comment(self,  blog_id, content):
        self.remote_api.comment(self.user_id, blog_id, content)

    def get_comments(self, blog_id):
        data = self.remote_api.get_comments(self.user_id, blog_id)
        comments = []
        if data is None: return comments
        for item in data:
            comment = Comment(item['commentId'], item['user']['userId'], item['user']['nickname'], item['content'], item['createTime'])
            comments.append(comment)
        return comments

    def get_follow_blogs(self):

        return self.remote_api.get_follow_blogs(self.user_id)

    def get_new_blogs(self):
        data = self.remote_api.get_new_blogs()
        return data
    
    def reflect(self):
        single_msg = self.memory.get_recent_memory()
        while True:
            reflect_message = copy.deepcopy(self.reflect_messages)
            tmp = {
                "role": "user",
                "content": single_msg
            }
            reflect_message.append(tmp)
            topics, retry = self.llm_api.get_reflect(reflect_message)
            if not retry:
                break
        self.topics = topics
    
    def choose_blog(self, blogs, recent_str):
        read_str = f"You have browsed {len(blogs)} Weibo posts, as follows:\n"
        cnt = 1
        for item in blogs:
            # read_str += f"{cnt}. {item.user_name} posted on Weibo on {item.create_date} saying \"{item.content}\"."
            user_name = self.remote_api.get_username(item['blog_id'])
            read_str += f"{cnt}. {user_name} post on Weibo on {item['create_date']} saying \"{item['content']}\"."
            read_str += f"#This weibo has {item['love']} likes, {item['replay_cnt']} retweets, and {len(item['comments'])} comments.\n"
            cnt += 1
        # {item.id} 可以指出weibo id
        while True:
            choose_message = copy.deepcopy(self.choose_messages)
            got = {
                "role": "assistant",
                "content": "I got it！"
            }
            recent = {
                "role": "user",
                "content": recent_str
            }
            read = {
                "role": "assistant", ##ernie 把user暂时改为assistant
                "content": read_str
            }
            quest = { 
                "role": "user",
                #"content": "请你按照以上例子的格式进行回复：\n我的选择为：\n"
                "content": 
                '''
                Choose from the following option，reply in JSON format, for example: \n
                ```
                {"My choice is":1},
                {"My choice is":2},
                {"My choice is":3}
                ```
                [Prohibit outputting irrelevant speech, only output JSON]
                '''
            }
            choose_message.append(got) #assistant
            choose_message.append(recent) #user
            choose_message.append(read) #assistant
            choose_message.append(quest) #user
            # print("*****************thread_person**************************")
            # print(choose_message)
            # print("*****************thread_person**************************")
            choose_id, retry = self.llm_api.get_blog_choose(choose_message)
            # print(choose_id)
            # print(type(choose_id))
            if retry:
                continue
            if '1' in choose_id:
                choose_id = 1
            elif '2' in choose_id:
                choose_id = 2
            elif '3' in choose_id:
                choose_id = 3
            elif '4' in choose_id:
                choose_id = 4
            elif '5' in choose_id:
                choose_id = 5
            else:
                choose_id = 1
            if choose_id <= len(blogs):
                return choose_id
    
    def notify_clock(self):
        with self.clock:
            self.clock.notifyAll()

    # def run(self):
    #     for _ in range(self.times):
    #         self.token, self.user_id = self.remote_api.login(self.name)
    #         with self.clock:  # 使用 clock 的 condition 等待
    #             self.clock.wait()  # 等待时间线程的通知
    #         start_time = time.time()  # 开始计时
    #         self.action(True)
    #         end_time = time.time()  # 结束计时
    #         duration = end_time - start_time
    #         print(f"Execution time for action in {self.name}: {duration:.3f} seconds")
    #         self.remote_api.logout(self.token)

    def run(self):
        self.user_id = self.remote_api.register_login(self.name)
        while True:
            with self.clock:  # 使用 clock 的 condition 等待
                self.clock.wait()  # 等待时间线程的通知
            start_time = time.time()  # 开始计时
            self.action(True)
            end_time = time.time()  # 结束计时
            duration = end_time - start_time
            print(f"Execution time for action in {self.name}: {duration:.3f} seconds")

    def get_offline_news(self):
        with open('offline_news.json', 'r', encoding='utf-8') as file:
            news_data = json.load(file)
        
        for news_item in news_data:
            news_time = datetime.datetime.strptime(news_item["time"], "%Y.%m.%d %H:%M:%S")
            if (Person.current_time-news_time).total_seconds() <= 3600: #一小时内的offline_news
                return news_item["news"]
        
        return ""

    #加入概率的action
    def action(self, show=False):
        prob = self.check_time()
        if prob == 0:
            return  # 如果概率为0，直接返回，不执行后续操作

        if self.name == "1111111111":
            with open('offline_news.json', 'r', encoding='utf-8') as file:
                news_data = json.load(file)
            for news_item in news_data:
                news_time = datetime.datetime.strptime(news_item["time"], "%Y.%m.%d %H:%M:%S")
                if (Person.current_time-news_time).total_seconds() <= 3600: #一小时内的offline_news  
                    post_content = news_item["news"]
                    self.post_weibo(post_content)
            return

        # if not self.plan():
        #     time.sleep(25)
        #     return
        #self.reflect() #添加反思，了解最近的主题
        print("1")
        start_time = time.time()
        recent_str = self.memory.get_recent_memory(5)
        end_time = time.time()
        print(f"get_recent_memory time: {end_time-start_time}")
        start_time = time.time()
        follow_blogs = self.get_follow_blogs()
        print("follow_blogs:", follow_blogs)
        end_time = time.time()
        print(f"get_follow_blogs time: {end_time-start_time}")
        start_time = time.time()
        all_blogs = self.get_new_blogs()
        print("all_blogs:", all_blogs)
        end_time = time.time()
        print(f"get_new_blogs time: {end_time-start_time}")
        offline_news = self.get_offline_news() # offline news (str)
        # 根据概率决定是否加入all_blogs中的文章
        if random.random() < 0.2:
            check_blogs = follow_blogs[:4] + all_blogs[:2] 
            print("all_blogs are read")
        else:
            check_blogs = follow_blogs[:4]
            # print("check_blogs:", check_blogs)
            print("no all_blogs")

        recent_blogs = []
        for blog in check_blogs:
            # blog_id = blog.blog_id
            blog_id = blog['blog_id']
            print(f"blog_id is {blog_id}." )
            # 决定是否阅读此博客 
            if blog_id in self.read_blog_ids: #若已读
                if random.random() < 0.3:  # 已读文章再次阅读的概率为30%
                    print(f"{blog_id} is read again!")
                    recent_blogs.append(blog)
            else: #若未读
                self.read_blog_ids.add(blog_id)  # 添加一个set用来记录阅读过的blog_id
                print(f"{blog_id} is read for the first time!")
                recent_blogs.append(blog)

        if len(recent_blogs) == 0:
            print("read no blogs")
            return #停止后续所有操作了
        start_time = time.time()
        choosed_id = self.choose_blog(recent_blogs, recent_str)
        end_time = time.time()
        print(f"choose_blog time: {end_time-start_time}")
        new_blog = recent_blogs[choosed_id-1]
        current_time_str = f" Current time is {Person.current_time} \n " #时间线
        offline_news_str = f" offline news: {offline_news} \n "  #读入离线新闻
        love_str = f"This Weibo has {new_blog['love']} likes.\n"
        replay_str = f"This Weibo has {new_blog['replay_cnt']} retweets.\n"
        new_blog_comments = new_blog['comments'][:5]
        comment_list = f"This Weibo contains {len(new_blog_comments)} comments, as follows:\n"
        for comm in new_blog_comments:
            comment_list += f"{comm['time']}: {comm['user_id']} commented: {comm['content']} \n"
        comment_list = f"This Weibo contains {len(new_blog_comments)} comments" if len(new_blog_comments) == 0 else comment_list

        user_name1 = self.remote_api.get_username(new_blog['blog_id'])

        new_blog_prompt = f"You read the Weibo posted by {user_name1} on {new_blog['create_date']} titled \"{new_blog['content']}\".\n"
        start_time = time.time()
        embedding_curr = get_embedding(new_blog_prompt)
        end_time = time.time()
        print(f"get_embedding time: {end_time-start_time}")
        start_time = time.time()
        recent_relevent_str = self.memory.get_relevent_memory(embedding_curr)
        end_time = time.time()
        print(f"get relevent memory: {end_time-start_time}")
        new_blog_prompt += current_time_str
        #new_blog_prompt += offline_news_str
        new_blog_prompt += love_str
        new_blog_prompt += replay_str
        new_blog_prompt += comment_list
        #blog_user_id = new_blog.user_id

        while True:
            chat_message = copy.deepcopy(self.chat_messages)
            ##以下“收到”为ernie新添加
            accept = {
                "role": "assistant",
                "content": ""
            }

            got = {
                "role": "assistant",
                "content": ""
            }
            recent = {
                "role": "user",
                "content": recent_relevent_str
            }

            read = {
                "role": "user",
                "content": new_blog_prompt
            }
            
            topics = {
                "role": "user",
                "content": f"You recently learned about the following topics from Weibo: {self.topics}"

            }
            if(self.category == 1):
                quest = {
                    "role": "user",
                    #"content": f"请你按照以上'例子'中的格式进行回复：\n"
                    "content": 
                    '''
                    ###
                    Choose option,
                    If the blog is mind-blowing and jaw-dropping, then Post Weibo to share it, \n
                    If agreeing with the viewpoint, the most likely choices are direct retweet/retweet original text (each with a 50% probability), \n
                    If eager to express an opinion, then Comment, \n
                    If the time is not for browsing Weibo, then Skip \n
                    For more detailed action explanations, refer to the action explanations in the above prompt.) Choose one of the actions listed in the following JSON, \n
                    Must reply in the given JSON format \n
                    ```
                    {"My choice is":"A.Comment", "Content":"...(express your opinion)"}, 
                    ```
                    {"My choice is":"B.Like", "Content": ""},
                    ```
                    {"My choice is":"C.Skip", "Content": ""}, 
                    ```
                    {"My choice is":"D.Dislike", "Content": ""}, 
                    ```
                    {"My choice is":"E.Repost", "Content": "I think he's right."},
                    ```
                    {"My choice is":"F.Repost Original", "Content": "The original text is quite interesting."},
                    ``` 
                    {"My choice is":"G.Post Weibo", "Content": "...(express like a media worker)"}
                    ```
                    【Prohibit outputting irrelevant speech, only output JSON】
                    '''
                }
            else:
                quest = {
                    "role": "user",
                    #"content": f"请你按照以上'例子'中的格式进行回复：\n"
                    "content": 
                    '''
                    ###
                    Choose option,
                    If agreeing with the viewpoint, then choose Like\n
                    If disagreeing, then choose Dislike \n
                    For more detailed action explanations, refer to the action explanations in the above prompt.) Choose one of the actions listed in the following JSON, \n
                    Must reply in the given JSON format \n
                    ```
                    {"My choice is":"B.Like", "Content": ""},
                    ```
                    {"My choice is":"C.Skip", "Content": ""}, 
                    ```
                    {"My choice is":"D.Dislike", "Content": ""}, 
                    ```
                    【Prohibit outputting irrelevant speech, only output JSON】
                    '''
                }
            chat_message.append(got) #assistant
            chat_message.append(topics) #user
            chat_message.append(accept) ##################加的
            chat_message.append(recent) #user
            chat_message.append(accept)#################加的
            chat_message.append(read) #user
            chat_message.append(accept)####################加的
            chat_message.append(quest) #user
            start_time = time.time()
            if(self.llm_api != "qwen_api"):
                action, comment, retry = self.llm_api.get_action_comment(chat_message, CORE_ACTIONS)
            else:
                action, comment, retry = self.llm_api.get_action_comment(chat_message, COMMON_ACTIONS)
            end_time = time.time()
            print(f"get_action_comment time: {end_time-start_time}")
            if not retry:
                break
        #print(chat_message)

        timestamp = Person.current_time

        embed_query = f"At {Person.current_time}: You performed the {action} action on {user_name1}'s Weibo titled \"{new_blog['content']}\". The content is: {comment}"
        embedding = get_embedding(embed_query)
        self.memory.record(embedding, user_name1, new_blog['content'], action, comment, timestamp)
        
        if show:
            print(f"{self.name}'s choice is: {action}")
            if comment is not None:
                print(f"{self.name}'s content is: {comment}")
        ##
        # 添加记录到文件
        dialogue_message = f"{self.name} performed the {action} at {timestamp}: {comment}"
        self.record_to_file(dialogue_message)

        if 'A' in action: #评论
            start_time = time.time()
            Person.blog_interaction_count += 1  #计数
            self.comment(new_blog['blog_id'], comment)
            end_time = time.time()
            print(f"comment time: {end_time-start_time}")
        elif 'B' in action: #点赞
            Person.blog_interaction_count += 1 # 计数
            self.love(new_blog['blog_id'])

        elif 'C' in action: #跳过
            pass

        elif 'D' in action: #点踩
            Person.blog_interaction_count += 1 # 计数
            self.dislike(new_blog["blog_id"])


        elif 'E' in action: #直接转发

            Person.blog_interaction_count += 1  #计数
            org = new_blog['content'].split(">>>")[0].strip()
            comment = f"{org}>>>{comment}"
            self.replay_weibo(new_blog['blog_id'], comment)

        elif 'F' in action: #转发原文
            Person.blog_interaction_count += 1  #计数
            org = new_blog.new_content.split(">>>")[0].strip()
            comment = f"{org}>>>{comment}"
            if new_blog['replay_id'] is not None: #如果有源微博则转发源微博
                self.replay_weibo(new_blog['replay_id'], comment)
            else: # 否则直接转发
                self.replay_weibo(new_blog['blog_id'], comment)

        elif 'G' in action: #发布新微博
            start_time = time.time()
            Person.blog_interaction_count += 1  #计数
            self.post_weibo(comment)
            end_time = time.time()
            print(f"Post weibo time: {end_time-start_time}")
  
class Memory:  
    def __init__(self):  
        self.history = []
    
    def get_cos_similar(self, v1: list, v2: list):
        num = float(np.dot(v1, v2))  # 向量点乘
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)  # 求模长的乘积
        return 0.5 + 0.5 * (num / denom) if denom != 0 else 0
  
    def record(self, embedding, blog_user, blog_content, action, content, timestamp):
        key = (blog_user, blog_content, action, content, timestamp)
        item = {'key':key, 'value':embedding}
        self.history.append(item)
    
    def get_relevent_memory(self, embedding, top=20):
        recent_mem = self.history[-top:]
        sim_list = []
        for item in recent_mem:
            score = self.get_cos_similar(embedding, item['value'])
            k_v = {'score':score, 'content':item['key']}
            sim_list.append(k_v)
        sorted_data = sorted(sim_list, key=lambda x: x['score'])[-5:]
        recent_mem = [data['content'] for data in sorted_data]
        it = 1
        mem = f"You recently did the following {len(sorted_data)} related activities on Weibo:\n"
        it = 1
        for item in recent_mem:
            desc = f"{it}. At {item[-1]}: You performed the {item[2]} action on {item[0]}'s Weibo titled \"{item[1]}\". The content is: {item[3]} \n"
            mem += desc
            it += 1
        if it == 1:
            return "You haven't performed any operations on Weibo recently."
        else: return mem

  
    def get_recent_memory(self, top=10):  
        mem = "You recently did the following activities on Weibo:\n"
        recent_mem = self.history[-top:]
        it = 1
        for item in recent_mem:
            item_content = item['key']
            desc = f"{it}. At {item_content[-1]}: You performed the {item_content[2]} action on {item_content[0]}'s Weibo titled \"{item_content[1]}\". The content is: {item_content[3]} \n"
            mem += desc
            it += 1
        if it == 1:
            return "You haven't performed any operations on Weibo recently."
        else: return mem

