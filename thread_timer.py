import datetime
import threading
import time
from thread_person1 import Person

class Clock(threading.Thread):
    def __init__(self, update_interval, time_step, condition = None):
        super().__init__()
        self.update_interval = update_interval  # 更新间隔（秒）
        self.time_step = time_step  # 每次更新增加的时间（分钟）
        self.blog_activity_per_step = []  # 添加列表以记录每个时间步的博客活动
        self.condition = condition  # 添加 condition 参数
    def run(self):
        while True:
            time.sleep(self.update_interval)
            with threading.Lock():
                Person.current_time += datetime.timedelta(minutes=self.time_step)
                self.blog_activity_per_step.append(Person.blog_interaction_count)
                Person.blog_interaction_count = 0  # 重置计数器
                self.save_activity_to_file()
                print(f"Clock updated: {Person.current_time}")
                print(f"Blog activity steps: {self.blog_activity_per_step}")
            
            # 使用 condition 通知所有等待的 Person 线程
            with self.condition:
                self.condition.notify_all()

    def save_activity_to_file(self):
        # 指定保存路径
        file_name = "/data1/chuanshi/Heterogeneous Prediction Platform/DIALOGUE_LOG_NEW/blog_activity_log.txt"
        with open(file_name, "a") as file:
            file.write(f"{self.blog_activity_per_step}\n")