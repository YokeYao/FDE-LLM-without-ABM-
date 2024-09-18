from prompt_template import *
import random  
import string  
import datetime
import time
from blogs import Article
from comments import Comment
from loves import Love
import copy
from restfulAPI import RemoteAPI
from datetime import datetime
import json
import textwrap  
  
def wrap_text(text, width=20):  
    wrapper = textwrap.TextWrapper(width=width)  
    return "\n".join(wrapper.wrap(text=text)) 

class Static():  
    def __init__(self, name='root', remote_api:RemoteAPI=None):
        self.name = name
        self.remote_api = remote_api
        self.login()
    
    def login(self):
        self.token, self.user_id = self.remote_api.login(self.name)
    
    def logout(self):
        self.remote_api.logout(self.token)
    
    def post_weibo(self, content):  
        self.remote_api.post_weibo(self.token, content)
    
    def replay_weibo(self, blog_id, content):  
        self.remote_api.replay(self.token, blog_id, content)
    
    def get_loves(self, blog_id):
        data = self.remote_api.get_loves(self.token, blog_id)
        love_list = []
        if data is None: return love_list
        for item in data:
            love = Love(item['loveId'], item['user']['userId'], item['user']['nickname'], item['createTime'])
            love_list.append(love)
        return love_list
    
    def get_replays(self, blog_id):
        data = self.remote_api.get_replays(self.token, blog_id)
        replay_list = []
        if data is None: return replay_list
        for item in data:
            replay_list.append(item)
        return replay_list
    
    def get_comments(self, blog_id):
        comments = []
        currentPage = 1
        while True:
            data = self.remote_api.get_comments(self.token, blog_id, currentPage)
            if data is None: return comments
            for item in data:
                comment = Comment(item['commentId'], item['user']['userId'], item['user']['nickname'], item['content'], item['createTime'])
                comments.append(comment)
            currentPage += 1
  
    def get_my_blogs(self):
        my_blogs = []
        currentPage = 1
        while True:
            data = self.remote_api.get_my_blogs(self.token, currentPage)
            currentPage += 1
            if data is None: return my_blogs            
            for item in data:
                replay_id = None
                replay_content = None
                if 'relay' in item.keys():
                    replay_id = item['relay']['blogId']
                    replay_content = item['relay']['content']
                blog = Article(item['blogId'], self.user_id, self.name, item['content'], item['createDate'], replay_id, replay_content)
                blog.comments = self.get_comments(blog.blog_id)
                blog.loves = len(self.get_loves(blog.blog_id))
                blog.replays = len(self.get_replays(blog.blog_id))
                my_blogs.append(blog)
    
    def get_follow_blogs(self):
        follow_blogs = []
        currentPage = 1
        while True:
            data = self.remote_api.get_follow_blogs(self.token, currentPage)
            currentPage += 1
            if data is None: 
                return follow_blogs

            for item in data:
                replay_id = None
                replay_content = None
                if 'relay' in item.keys():
                    replay_id = item['relay']['blogId']
                    replay_content = item['relay']['content']
                blog = Article(item['blogId'], item['user']['userId'], item['user']['name'], item['content'], item['createDate'], replay_id, replay_content)
                blog.comments = self.get_comments(blog.blog_id)
                blog.loves = len(self.get_loves(blog.blog_id))
                blog.replays = len(self.get_replays(blog.blog_id))
                follow_blogs.append(blog)

    def get_new_blogs(self):
        new_blogs = []
        currentPage = 1
        while True:
            data = self.remote_api.get_new_blogs(currentPage)
            currentPage += 1
            if data is None: return new_blogs
            for item in data:
                replay_id = None
                replay_content = None
                if 'relay' in item.keys():
                    replay_id = item['relay']['blogId']
                    replay_content = item['relay']['content']
                blog = Article(item['blogId'], item['user']['userId'], item['user']['name'], item['content'], item['createDate'], replay_id, replay_content)
                blog.comments = self.get_comments(blog.blog_id)
                blog.loves = len(self.get_loves(blog.blog_id))
                blog.replays = len(self.get_replays(blog.blog_id))
                new_blogs.append(blog)
    
    def get_blog_by_id(self, blog_id):
        data = self.remote_api.get_blog_by_id(blog_id)
        if data is None: return None
        return data
    
    def get_fans(self, user_token):
        data = self.remote_api.get_follower_info(user_token)
        if data is None: return []
        return data
    
    def get_influence(self, user_token):
        comments, loves, replays = 0, 0, 0
        currentPage = 1
        while True:
            data = self.remote_api.get_my_blogs(user_token, currentPage)
            currentPage += 1
            if data is None: break           
            for item in data:
                comments += len(self.get_comments(item['blogId']))
                loves += len(self.get_loves(item['blogId']))
                replays += len(self.get_replays(item['blogId']))
        return comments, loves, replays

def static_user_network(static):
    while True:
        try:
            with open("user_info.json", "r") as infile:  
                user_info = json.load(infile)
            break
        except:
            time.sleep(5)
    
    nodes = []
    edges = []
    init_size = 10
    for key in user_info.keys():
        user_id = key
        user_name = user_info[key]["name"]
        user_token = user_info[key]["token"]
        try:
            fans = static.get_fans(user_token)
        except:
            return
        for fan in fans:
            edge = {"from":f'{fan["userId"]}', "to":user_id}
            edges.append(edge)
        try:
            comments, loves, replays = static.get_influence(user_token)
        except:
            return
        influence = comments + loves + replays * 2
        label = f"{user_name}:Like{loves}-Comment{comments}-Repost{replays}"
        nodes.append({"id": user_id, "label": label, "size":init_size+influence})
    network_data = {"nodes": nodes, "edges": edges}
    with open("network_data.json", "w") as outfile:  
        json.dump(network_data, outfile)

def static_blogs_network(static):
    nodes = []
    edges = []
    init_size = 10
    blogs = static.get_new_blogs()
    for blog in blogs:
        label = f"Time:{blog.create_date} Author:{blog.user_name} \n Content:{blog.content}"
        label = wrap_text(label)  
        label += f"\n Like:{blog.loves} Comment:{len(blog.comments)} Repost:{blog.replays}"
        influence = blog.loves + len(blog.comments) + blog.replays * 2
        node = {"id": f"{blog.blog_id}", "label": label, "size":init_size+influence}
        nodes.append(node)
        if blog.replay_id is not None:
            edge = {"from":f'{blog.blog_id}', "to":f'{blog.replay_id}'}
            edges.append(edge)
    
    blogs_data = {"nodes": nodes, "edges": edges}
    with open("blogs_data.json", "w") as outfile:  
        json.dump(blogs_data, outfile)

def static_run(ip, port):
    remote_api = RemoteAPI(ip, port)
    static = Static(remote_api=remote_api)
    blogs = static.get_new_blogs()
    cnt = 1
    for blog in blogs:
        print(f"{cnt}. {blog.blog_id} Time:{blog.create_date} Author:{blog.user_name} \n Content:{blog.content} \n Like:{blog.loves} Comment:{len(blog.comments)} Repost:{blog.replays}")
        cnt += 1
    while True:
        static.login()
        static_user_network(static)
        static_blogs_network(static)
        time.sleep(10)
        static.logout()

if __name__ == '__main__':
    static_run()
    
    
    
