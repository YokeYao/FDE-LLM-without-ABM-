import threading
import datetime
import random

class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        self.follows = []
        self.blogs = []
        self.lock = threading.Lock()

class Post:
    def __init__(self, post_id, content, create_date, replay_id):
        self.post_id = post_id
        self.content = content
        self.create_date = create_date
        self.replay_id = replay_id  # 如果是转发，这里会有ID，原创则为空字符串
        self.comments = []
        self.love = 0
        self.dislike = 0
        self.replay_cnt = 0
        self.lock = threading.Lock()

class Comment:
    def __init__(self, user, content, time):
        self.user = user
        self.content = content
        self.time = time
        self.lock = threading.Lock()

class Weibo(User, Post, Comment):
    def __init__(self):
        super().__init__(user_id="", user_name="")
        self.all_blogs = {}
        self.new_blogs = []
        self.users = {}
        # user
        self.lock = threading.Lock()

    def generate_user_id(self):
        return str(random.randint(100000, 999999))

    def generate_blog_id(self):
        return  str(random.randint(100000000, 999999999))

    def generate_love_id(self):
        return str(random.randint(1000, 9999))

    def generater_dislike_id(self):
        return  str(random.randint(100, 999))

    def register_login(self, user_name):
        # 注册登录
        with self.lock:
            # 检查用户是否已注册
            for user_id, user_info in self.users.items():
                if user_info['user_name'] == user_name:
                    return user_id  # 返回已注册用户的ID

            # 若用户未注册，则生成新的用户ID并注册
            user_id = self.generate_user_id()
            self.users[user_id] = {'user_name': user_name, 'follow': [], 'blogs': []}
            print("REGISTER INFO:", self.users)
            return user_id  # 返回新注册用户的ID

    def follow(self, follower_id, followee_id):
        # 关注用户
        with self.lock:
            if follower_id == followee_id:
                # 自己不能关注自己
                print("自己不能关注自己")
                return False
            if followee_id in self.users and follower_id in self.users:
                self.users[followee_id]['follow'].append(follower_id)
                print("USER INFO:", self.users)
                return True
            return False

    def post_weibo(self, user_id, content):
        # 发微博
        with self.lock:
            # 生成微博ID
            weibo_id = self.generate_blog_id()

            # 添加微博到用户信息中
            post_info = {
                "blog_id": weibo_id,
                "content": content,
                "create_date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "replay_id": "",
                "comments": [],
                "love": 0,
                "replay_cnt": 0,
                "dislike": 0
            }

            # 添加微博到用户微博列表中
            user_blogs = self.users[user_id]['blogs']
            user_blogs.append(post_info)

            # 获取微博在用户微博列表中的索引位置
            index = len(user_blogs) - 1

            # 更新 self.all_blogs 字典
            self.all_blogs[weibo_id] = [user_id, index]

            # print("所有微博：" , self.all_blogs)

            # 更新 self.new_blogs 列表，确保长度不超过 10
            self.new_blogs.append(weibo_id)
            if len(self.new_blogs) > 10:
                oldest_weibo_id = self.new_blogs.pop(0)

            print("POST SUCCEED, THE INFO IS：", post_info)

            return weibo_id

    def replay(self, user_id, post_id, content):
        # 转发微博
        with self.lock:
            if post_id in self.all_blogs:
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                original_post = self.users[user_id_of_post]['blogs'][index_of_post]

                replay_id = self.generate_blog_id()

                replay_info = {
                    "blog_id": replay_id,
                    "content": original_post['content'],
                    "create_date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                    "replay_id": post_id,  # replay_id保持不变
                    "comments": original_post['comments'][:],  # 复制原微博的评论列表
                    "love": original_post['love'],  # 复制原微博的点赞次数
                    "replay_cnt": original_post['replay_cnt'] + 1,  # 增加原微博的转发次数
                    "dislike": original_post['dislike']
                }

                # 添加新的评论
                replay_info['comments'].append({
                    "user_id": user_id,
                    "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                    "content": content
                })

                user_blogs = self.users[user_id]['blogs']
                user_blogs.append(replay_info)

                index = len(user_blogs) - 1

                self.all_blogs[replay_id] = [user_id, index]

                # 将转发微博添加到 all_blogs 中
                self.all_blogs[replay_id] = [user_id, index]

                # 将转发微博添加到 new_blogs 中
                self.new_blogs.append(replay_id)

                # original_post['replay_cnt'] += 1
                original_post['replay_cnt'] += 1

                print("转发微博信息：", replay_info)
                print("原始微博转发数更新为：", original_post['replay_cnt'])

                return replay_id
            else:
                print("微博不存在")
                return None

    def get_replay(self):
        # 获得转发微博的信息列表
        with self.lock:
            replay_blogs = []

            for user_id, user_info in self.users.items():
                for blog in user_info['blogs']:
                    if blog['replay_id'] and blog['replay_id'] != blog['blog_id']:
                        replay_blogs.append(blog)

        return replay_blogs

    # def love(self, user_id, post_id):
    #     # 点赞
    #     with self.lock:
    #         if post_id in self.all_blogs:
    #             # 获取微博的信息
    #             user_id_of_post, index_of_post = self.all_blogs[post_id]
    #             post = self.users[user_id_of_post]['blogs'][index_of_post]
    #
    #             # 初始化微博的点赞用户列表
    #             if 'love_users' not in post:
    #                 post['love_users'] = []
    #
    #             # 检查用户是否已经点过赞
    #             if user_id not in post['love_users']:
    #                 # 增加微博的点赞数量
    #                 post['love'] += 1
    #
    #                 # 将用户加入点赞列表中
    #                 post['love_users'].append(user_id)
    #
    #                 # print("被点赞的微博信息:")
    #                 # print("微博ID:", post_id)
    #                 # print("内容:", post['content'])
    #                 # print("作者:", self.users[user_id_of_post]['user_name'])
    #                 # print("点赞数:", post['love'])
    #                 # print("点赞用户列表:", post['love_users'])
    #
    #                 return True
    #             else:
    #                 return False  # 用户已经点过赞了
    #         else:
    #             return False  # 微博不存在

    def love(self, user_id, post_id):
        # 点赞
        with self.lock:
            if post_id in self.all_blogs:
                # 获取微博的信息
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                post = self.users[user_id_of_post]['blogs'][index_of_post]

                # 初始化微博的点赞用户列表
                if 'love_users' not in post:
                    post['love_users'] = []

                # 检查用户是否已经点过赞
                if user_id not in post['love_users']:
                    # 生成点赞ID和创建时间
                    love_id = self.generate_love_id()
                    created_time = datetime.datetime.now().isoformat()

                    # 增加微博的点赞数量
                    post['love'] += 1

                    # 将用户加入点赞列表中，并记录点赞ID和创建时间
                    post['love_users'].append({
                        'user_id': user_id,
                        'love_id': love_id,
                        'created_time': created_time
                    })

                    # print("被点赞的微博信息:")
                    # print("微博ID:", post_id)
                    # print("内容:", post['content'])
                    # print("作者:", self.users[user_id_of_post]['user_name'])
                    # print("点赞数:", post['love'])
                    # print("点赞用户列表:", post['love_users'])

                    return True
                else:
                    return False  # 用户已经点过赞了
            else:
                return False  # 微博不存在

    def get_loves(self, post_id):
        # 获得微博的点赞用户列表
        with self.lock:
            if post_id in self.all_blogs:
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                return self.users[user_id_of_post]['blogs'][index_of_post]['love_users']
            else:
                return None  # 微博不存在

    def dislike(self, user_id, post_id):
        # 点赞
        with self.lock:
            if post_id in self.all_blogs:
                # 获取微博的信息
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                post = self.users[user_id_of_post]['blogs'][index_of_post]

                # 初始化微博的点赞用户列表
                if 'dislike_users' not in post:
                    post['dislike_users'] = []

                # 检查用户是否已经点过赞
                if user_id not in post['dislike_users']:
                    # 生成点赞ID和创建时间
                    dislike_id = self.generate_love_id()
                    created_time = datetime.datetime.now().isoformat()

                    # 增加微博的点赞数量
                    post['dislike'] += 1

                    # 将用户加入点赞列表中，并记录点赞ID和创建时间
                    post['dislike_users'].append({
                        'user_id': user_id,
                        'dislike_id': dislike_id,
                        'created_time': created_time
                    })

                    return True
                else:
                    return False  # 用户已经点过赞了
            else:
                return False  # 微博不存在

    def get_dislikes(self, post_id):
        # 获得微博的点赞用户列表
        with self.lock:
            if post_id in self.all_blogs:
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                return self.users[user_id_of_post]['blogs'][index_of_post]['dislike_users']
            else:
                return None  # 微博不存在

    def comment(self, user_id, post_id, content):
        # 评论
        with self.lock:
            if post_id in self.all_blogs:
                # 获取微博的信息
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                post = self.users[user_id_of_post]['blogs'][index_of_post]


                # 生成评论时间
                comment_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

                # 构建评论
                comment_info = {
                    "user_id": user_id,
                    "time": comment_time,
                    "content": content
                }

                # 将评论添加到微博的评论列表中
                post['comments'].append(comment_info)

                print("comment_info:", comment_info)

                # 在用户信息中记录评论
                # for user_info in self.users.values():
                #     for blog in user_info['blogs']:
                #         if blog['post_id'] == post_id:
                #             blog['comments'].append(comment_info)

                return True
            else:
                return False  # 微博不存在

    def get_comments(self, post_id):
        # 获得微博评论列表
        with self.lock:
            if post_id in self.all_blogs:
                # 获取微博的信息
                user_id_of_post, index_of_post = self.all_blogs[post_id]
                post = self.users[user_id_of_post]['blogs'][index_of_post]

                # 返回微博的评论列表
                return post['comments']
            else:
                return None  # 微博不存在

    def get_follow_blogs(self, user_id):
        # 得到关注的用户的微博
        with self.lock:
            if user_id in self.users:
                followee_ids = self.users[user_id]['follow']
                follow_blogs = []

                # 遍历关注列表的用户ID
                for followee_id in followee_ids:
                    # 检查关注的用户是否存在
                    if followee_id in self.users:
                        # 获取关注用户的微博信息
                        followee_blogs = self.users[followee_id]['blogs']
                        # 将关注用户的微博信息添加到结果中
                        follow_blogs.extend(followee_blogs)

                # 对结果按照创建日期进行排序
                follow_blogs.sort(key=lambda x: x['create_date'])

                print("follow_blogs:",follow_blogs)

                return follow_blogs
            else:
                return None  # 用户不存在

    # def get_new_blogs(self):
    #     with self.lock:
    #         return self.new_blogs

    def get_new_blogs(self):
        blog_info_list = []

        for blog_id in self.new_blogs:
            # 从 all_blogs 中找到对应的 userid 和 idx
            if blog_id in self.all_blogs:
                userid, idx = self.all_blogs[blog_id]
                # 从 user 中找到对应的用户
                if userid in self.users:
                    user_info = self.users[userid]
                    # 从用户的博客列表中找到对应的微博信息
                    if 'blogs' in user_info and idx < len(user_info['blogs']):
                        blog_info = user_info['blogs'][idx]
                        blog_info_list.append(blog_info)

        return blog_info_list

    def get_weibo_structure(self):
        # weibo数据结构输出
        with self.lock:
            structure = {
                "all_blogs": self.all_blogs,
                "new_blogs": self.new_blogs,
                "users": self.users
            }
            return structure

    def get_username(self, blog_id):
        # 检查blog_id是否存在
        if blog_id in self.all_blogs:
            # 获取对应的userid
            userid, _ = self.all_blogs[blog_id]
            # 检查userid是否存在
            if userid in self.users:
                # 返回对应的用户名
                return self.users[userid]['user_name']
        # 如果blog_id不存在，返回None或者相应的提示信息
        return None








