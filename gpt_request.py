import json
import ollama
import random
import time
import requests
import re
from pydantic import BaseModel
from typing import List, Iterator
from qwen_agent.llm.base import BaseChatModel
from qwen_agent.llm.schema import Message, ContentItem
from abc import ABC, abstractmethod
from qwen_agent import Agent

from typing import Dict, Iterator, List, Optional, Union
from qwen_agent.llm import BaseChatModel
from qwen_agent.tools import BaseTool
from qwen_agent.utils.utils import has_chinese_chars

base_url = "http://127.0.0.1:8215" # 本地部署的地址,或者使用你访问模型的API地址
# remote ip "http://221.13.81.179:60113"

def remove_last_comma_and_trailing_special_chars(json_str):  
    # 移除字符串末尾的空白字符（包括空格、制表符、换行符等）  
    json_str = json_str.rstrip()  
      
    # 使用正则表达式找到最后一个逗号的位置（忽略逗号后面的空白字符）  
    last_comma_index = re.search(r',(?:\s*)$', json_str)  
      
    # 如果找到了最后一个逗号，就移除它及其后面的空白字符  
    if last_comma_index:  
        json_str = json_str[:last_comma_index.start()] + json_str[last_comma_index.end():]  
      
    return json_str  

def get_embedding(text):
    text = text.replace("\n", " ")
    if not text: 
        text = "this is blank"
    # The data payload for the POST request
    data = {
        "input": text,
    }
    response = requests.post(f"{base_url}/v1/embeddings", json=data, verify=False)
    decoded_line = response.json()
    content = decoded_line.get("data", [{}])[0].get("embedding", "")
    return content

class ERNIEAPI():
    def __init__(self):
        self.API_KEY = "D48VQStJHIxqWlv56iFVpoDi"
        self.SECRET_KEY = "QtkapnrFklzZrZ8PAaRKo2BYooNgGkq5"
    
    def get_access_token(self):

        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))

    def ERNIE_run(self, prompt):
        # print("******prompt*********")  #ernie要求prompt首位为user，odd index为assistent
        # print(prompt)
        # print("******prompt*********")
        access_token = self.get_access_token()
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + access_token
        payload = json.dumps({
        "messages": prompt,
        "reponse_format": ".json_object",
        "temperature": 0.8,
        "penalty_score": 1

        })
        
        headers = {
            'Content-Type': 'application/json'
        }
    
        response = requests.request("POST", url, headers=headers, data=payload)
        # print("response*************")
        # print(response.text)
        # print("response*************")
        # print()
        output = response.json()
        # print()
        # print("***********output************")
        # print(output)
        # print("***********output************")
        return output['result']
    
    def temp_sleep(self, seconds=0.1):
        time.sleep(seconds)

    def get_action_comment(self, prompt, ACTIONS):
        ans = self.ERNIE_run(prompt)
        action = None
        comment = None
        retry = False
        #'''
        print('action---------------------')
        print(prompt)
        print('action ans------------------------')
        print(ans)
        print('action end')
        #'''
        # 分割回复中的每一行，并遍历以寻找行动和评论
        try:
            matches = re.findall(r'\{(.*?)\}', ans, re.DOTALL)
            matches = "{" + matches[0] + "}"
            matches = matches.replace("'", "\"")
            matches = remove_last_comma_and_trailing_special_chars(matches)
            try:
                json_data = json.loads(matches)
                action = str(json_data['我的选择为'])
                comment = str(json_data['内容'])
            except:
                action = None
        except:
            action = None
    
        # # 如果行为或评论没有被成功解析，可能需要重试
        if action is None or action not in ACTIONS or action == "":
            retry = True
        else:
            if 'A' in action or 'H' in action:
                if comment is None or comment =="":
                    retry = True
            if 'D' in action:
                if comment is None or comment =="":
                    comment = "直接转发"
            if 'E' in action:
                if comment is None or comment =="":
                    comment = "转发原文"
        
        return action, comment, retry

    def get_reflect(self, prompt):
        ans = self.ERNIE_run(prompt)
        topics = None
        retry = False
        # 分割回复中的每一行，并遍历以寻找行动和评论
        lines = ans.strip().split('\n')
        for line in lines:
            if line.startswith("主题为："):
                topics = line.split("：")[-1].strip()
    
        # # 如果行为或评论没有被成功解析，可能需要重试
        if topics is None:
            retry = True
    
        return topics, retry
    
    def get_blog_choose(self, prompt):
        ans = self.ERNIE_run(prompt)
        choose_id = None
        retry = False
        #'''
        print('choose---------------------')
        print(prompt)
        print('choose ans------------------------')
        print(ans)
        print('choose end')
        #'''
        try:
            matches = re.findall(r'\{(.*?)\}', ans, re.DOTALL)
            matches = "{" + matches[0] + "}"
            matches = matches.replace("'", "\"")
            matches = remove_last_comma_and_trailing_special_chars(matches)
            try:
                json_data = json.loads(matches)
                choose_id = str(json_data['我的选择为'])
            except:
                choose_id = None
        except:
            choose_id = None
        # # 如果行为或评论没有被成功解析，可能需要重试
        if choose_id is None or choose_id=="":
            retry = True
    
        return choose_id, retry

class ChatGLMAPI:
    def __init__(self, ip_address="127.0.0.1", port="8215"):  
        self.base_url = f"http://{ip_address}:{port}"
        self.model = "chatglm3-6b"

    def create_chat_completion(self, messages, use_stream=False, re=False):
        data = {
            "model": self.model, # 模型名称
            "messages": messages, # 会话历史
            "stream": use_stream, # 是否流式响应
            "max_tokens": 500, # 最多生成字数
            "temperature": 0.8, # 温度
            "top_p": 0.8, # 采样概率
        }
        response = requests.post(f"{self.base_url}/v1/chat/completions", json=data, stream=use_stream)
        if response.status_code == 200:
            if use_stream:
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')[6:]
                        try:
                            response_json = json.loads(decoded_line)
                            content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            #print(content)
                        except:
                            print("Special Token:", decoded_line)
            else:
                # 处理非流式响应
                decoded_line = response.json()
                content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
                if re:
                    return content
                else:
                    print(decoded_line)
                    print(content)
        else:
            print("Chat-GLM3 Error:", response.status_code)
            return None

    def temp_sleep(self, seconds=0.1):
        time.sleep(seconds)

    def ChatGLM_single_request(self, prompt): 
        # print(type(prompt)) list
        self.temp_sleep()
        completion = self.create_chat_completion(prompt, use_stream=False, re=True)
        return completion
    
    def get_action_comment(self, prompt, ACTIONS):
        ans = self.ChatGLM_single_request(prompt)
        action = None
        comment = None
        retry = False
        #'''
        print('action---------------------')
        print(prompt)
        print('action ans------------------------')
        print(ans)
        print('action end')
        #'''
        # 分割回复中的每一行，并遍历以寻找行动和评论

        try:
            matches = re.findall(r'\{([^}]*)\}', ans, re.DOTALL)
            if matches:
                json_data = json.loads("{" + matches[0] + "}")
                action = json_data.get("My choice is")
                comment = json_data.get("Content")
        except Exception as e:
            print("Error:", e)
            action = None

        print(action)

        # # 如果行为或评论没有被成功解析，可能需要重试
        if action is None or action not in ACTIONS or action == "":
            retry = True
            print("retry action")
        else:
            if 'A' in action or 'F' in action:
                if comment is None or comment =="":
                    retry = True
                    print("retry A/F")
            if 'D' in action:
                if comment is None or comment =="":
                    comment = "Repost"
            if 'E' in action:
                if comment is None or comment =="":
                    comment = "Repost Original"
        
        return action, comment, retry

    def get_reflect(self, prompt):
        ans = self.ChatGLM_single_request(prompt)
        topics = None
        retry = False
        # 分割回复中的每一行，并遍历以寻找行动和评论
        lines = ans.strip().split('\n')
        for line in lines:
            if line.startswith("The topic is："):
                topics = line.split("：")[-1].strip()
    
        # # 如果行为或评论没有被成功解析，可能需要重试
        if topics is None:
            retry = True
    
        return topics, retry
    
    def get_blog_choose(self, prompt):
        ans = self.ChatGLM_single_request(prompt)
        choose_id = None
        retry = False  
        #'''
        print('choose---------------------')
        print(prompt)
        print('choose ans------------------------')
        print(ans)
        print('choose end')
        #'''
        try:
            matches = re.findall(r'\{(.*?)\}', ans, re.DOTALL)
            matches = "{" + matches[0] + "}"
            matches = matches.replace("'", "\"")
            matches = remove_last_comma_and_trailing_special_chars(matches)
            try:
                json_data = json.loads(matches)
                choose_id = str(json_data['My choice is'])
            except:
                choose_id = None
        except:
            choose_id = None
        # # 如果行为或评论没有被成功解析，可能需要重试
        if choose_id is None or choose_id == "":
            retry = True

        return choose_id, retry

class QwenturboAPI(Agent):
    default_llm_cfg = {
        'model': 'qwen-turbo',
        'model_server': 'dashscope',
        'api_key': 'sk-9b34df5920894a27af280fb7a5111c55'
    }

    def __init__(self, llm_cfg=None):
        if llm_cfg is None:
            llm_cfg = self.default_llm_cfg 
        super().__init__(llm=llm_cfg, name="Qwen Chat Agent", description="A specialized agent for handling Qwen model interactions.")
    
    def _run(self, messages: List[Message], lang: str = 'en', **kwargs) -> Iterator[List[Message]]:
        #检查llm_cfg有没有正确传入
        # print('************llm_cfg2**************************')
        # if self.llm is None:
        #     print('none')
        # else:
        #     print(self.llm)
        # print('************llm_cfg2**************************')
        return self._call_llm(messages=messages)
        
    def temp_sleep(self, seconds=0.5):
        time.sleep(seconds)

    def single_request(self, prompt):
        self.temp_sleep()
        string_list = [str(d) for d in prompt] #因为cotent只能要字符串，所以先把列表里的字典转成字符串，再连接在一起
        joined_prompt = ', '.join(string_list)

        messages = [Message(role='user', content=joined_prompt)]
        
        ###
        # print("*****single_request1****")
        # for message in messages:      
        #     print(message.role)
        #     print(type(message.content))
        #     print(len(message.content))
        # print("*****single_request1****")
        ###
        responses = self.run(messages)##这一步成功了且role和content都没问题
        #print(responses)
        for response in responses:
            for msg in response:
                continue
        out = msg.role + msg.content
        #print(out)
        #print(type(out))
        return out

    def get_action_comment(self, prompt, ACTIONS):
        #print("运行了action")
        ans = self.single_request(prompt)
        action = None
        comment = None
        retry = False
        #'''
        print('action---------------------')
        print(prompt)
        print('action ans------------------------')
        print(ans)
        print('action end')
        #'''
        # 分割回复中的每一行，并遍历以寻找行动和评论
        
        try:    
            matches = re.findall(r'\{([^}]*)\}', ans, re.DOTALL)
            if matches:
                json_data = json.loads("{" + matches[0] + "}")
                action = json_data.get("My choice is")
                comment = json_data.get("Content")
        except Exception as e:
            print("Error:", e)
            action = None
        print(action)
        # # 如果行为或评论没有被成功解析，可能需要重试
        if action is None or action not in ACTIONS or action == "":
            retry = True
        else:
            if 'A' in action or 'H' in action:
                if comment is None or comment =="":
                    retry = True
            if 'D' in action:
                if comment is None or comment =="":
                    comment = "Repost"
            if 'E' in action:
                if comment is None or comment =="":
                    comment = "Repost Original"
        
        return action, comment, retry

    def get_reflect(self, prompt):
        ans = self.single_request(prompt)
        topics = None
        retry = False
        # 分割回复中的每一行，并遍历以寻找行动和评论
        lines = ans.strip().split('\n')
        for line in lines:
            if line.startswith("The topic is:"):
                topics = line.split(":")[-1].strip()
    
        # # 如果行为或评论没有被成功解析，可能需要重试
        if topics is None:
            retry = True
    
        return topics, retry
    
    # def get_blog_choose(self, prompt):
        # ans = self.single_request(prompt)
        # print(ans)
        # choose_id = None
        # retry = False
        # #'''
        # print('choose---------------------')
        # print(prompt)
        # print('choose ans------------------------')
        # print(ans)
        # print('choose end')
        # #'''
        # try:
        # # 修改正则表达式以匹配assistant后的大括号内内容
        #     matches = re.findall(r'assistant\{(.*?)\}', ans, re.DOTALL)
        #     if matches:
        #         matches = "{" + matches[0] + "}"
        #         matches = matches.replace("'", "\"")
        #         matches = remove_last_comma_and_trailing_special_chars(matches)
        #         try:
        #             json_data = json.loads(matches)
        #             choose_id = str(json_data['My choice is'])
        #         except:
        #             choose_id = None
        #     else:
        #         choose_id = None
        # except:
        #     choose_id = None
        # #print(choose_id)  # None 字符串
        # # # 如果行为或评论没有被成功解析，可能需要重试
        # if choose_id is None or choose_id=="" : #or choose_id == "None":
        #     retry = True
        # return choose_id, retry

    def get_blog_choose(self, prompt):
        ans = self.single_request(prompt)
        choose_id = "1"
        retry = False 
        return choose_id, retry

class OllamaAPI():
    def __init__(self):  
        self.model = "gemma:7b-instruct-v1.1-fp16" # ollama run qwen:0.5b-chat-v1.5-fp16
                                                # ollama run qwen:1.8b-chat-v1.5-fp16
                                                # ollama run gemma:7b-instruct-v1.1-fp16

    def run(self, messages):
        return ollama.chat(self.model, messages)

    def temp_sleep(self, seconds=0.1):
        time.sleep(seconds)

    def single_request(self, prompt): 
        self.temp_sleep()
        response = self.run(prompt)
        return response['message']['content']
    
    def get_action_comment(self, prompt, ACTIONS):
        ans = self.single_request(prompt)
        action = None
        comment = None
        retry = False
        #'''
        print('action---------------------')
        print(prompt)
        print('action ans------------------------')
        print(ans)
        print('action end')
        #'''
        # 分割回复中的每一行，并遍历以寻找行动和评论

        try:
            matches = re.findall(r'\{([^}]*)\}', ans, re.DOTALL)
            if matches:
                json_data = json.loads("{" + matches[0] + "}")
                action = json_data.get("My choice is")
                comment = json_data.get("Content")
        except Exception as e:
            print("Error:", e)
            action = None

        print(action)

        # # 如果行为或评论没有被成功解析，可能需要重试
        if action is None or action not in ACTIONS or action == "":
            retry = True
            print("retry action")
        else:
            if 'A' in action or 'F' in action:
                if comment is None or comment =="":
                    retry = True
                    print("retry A/F")
            if 'D' in action:
                if comment is None or comment =="":
                    comment = "Repost"
            if 'E' in action:
                if comment is None or comment =="":
                    comment = "Repost Original"
        
        return action, comment, retry

    def get_reflect(self, prompt):
        ans = self.single_request(prompt)
        topics = None
        retry = False
        # 分割回复中的每一行，并遍历以寻找行动和评论
        lines = ans.strip().split('\n')
        for line in lines:
            if line.startswith("The topic is："):
                topics = line.split("：")[-1].strip()
    
        # # 如果行为或评论没有被成功解析，可能需要重试
        if topics is None:
            retry = True
    
        return topics, retry
    
    def get_blog_choose(self, prompt):
        ans = self.single_request(prompt)
        choose_id = "1"
        retry = False 

        return choose_id, retry
#           Qwen 0.5b测试
if __name__ == '__main__':
    llm_api = Qwen05bAPI()
    prompt = [{
                "role": "user",
                "content": "can u say hello?"
            }]
    response = llm_api.single_request(prompt)
    print(response)
#            GLM 测试
# if __name__ == '__main__':
#     prompt = [{
#                 "role": "system",
#                 "content": "用python写hello"
#             }]
#     print(prompt)
#     llm_api = ChatGLMAPI()
#     response = llm_api.ChatGLM_single_request(prompt)
#     #response = get_embedding('wirte a python code for float addctive')
#     print(response)

#               Qwen测试

# if __name__ == '__main__':
#     qwen_api = QwenAPI()   
#     messages = [
#         Message(role='user', content='1+1=?', name='User')
#     ]


# #      ernie测试
# if __name__ == '__main__':
#     ernie_api = ERNIEAPI()     
#     prompt = [
#                 {'role': 'user', 
#                 'content': """

#                 }]
                
#     rawdata = ernie_api.ERNIE_run(prompt)
#     print(rawdata)
