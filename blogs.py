class Article:  
    def __init__(self, blog_id, user_id, user_name, content, create_date, replay_id=None, replay_content=None):
        self.replay_id = replay_id
        self.blog_id = blog_id
        self.user_id = user_id
        self.user_name = user_name
        self.replay_content = replay_content
        self.new_content = content
        self.content = ""
        if replay_id is not None:
            self.content += f"##The content of the original Weibo being reposted is: {replay_content} \n"
            self.content += "The content of this Weibo is:\n"
        self.content += content
        from thread_person import Person #把create_date与时钟相统一
        self.create_date = Person.current_time
        self.comments = []  
        self.loves = 0  
        self.replays = 0  
  
    def comment(self, comment):  
        self.comments.append(comment) 
  
    def love(self):  
        self.loves += 1  
  
    def replay(self):  
        self.replays += 1   
  
    def get_stats(self):  
        return {  
            "blog_id": self.blog_id,
            "comments": len(self.comments),  
            "loves": self.loves,   
            "replays": self.replays,
            "create_date": self.create_date,
        }  
    
    