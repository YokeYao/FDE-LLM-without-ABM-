import json
from gpt_request import ChatGLMAPI
from tqdm import tqdm
# Initialize the API
chatglm_api = ChatGLMAPI()
# Load the content from the JSON file
with open('user_content2.json', 'r') as file:
    data = json.load(file)

# # Iterate over the contents, translate it, and update the content
for item in tqdm(data, desc="Generating profile...", unit='item'):
    id = item['user_id']
    content = item['content']

    prompt = [{
        "role": "user",
        "content": f"""
###

You are now a user personality analyst. I will provide three historical posts from a user, and descriptions of five communication roles, then you need to complete the user's social character profile.

###
userid: {id}

Historical posts: 
{content}

###
Communication role：
1 Idea Starter 
These can be considered as an individual who starts a 
conversational meme. They tend to be highly engaged with the 
media, in the on- and off-line environment. They utilize multiple 
sources of social media, but have an intricate network of trusted 
relationships, especially online. As a result of this, their network 
of connections is usually limited, but this ensures that the 
connections are of high quality 
Although Idea Starters may not be the one with the ‘bright idea’, 
they are the ones which start the conversation, and due to its 
trusted connections, are in a fertile environment for the idea to 
grow. 
2 Amplifier 
These can be considered as an individual who collates multiple 
thoughts and shares ideas and opinions. Amplifiers thrive off 
sharing opinions of others; enjoy being the first to do so. They 
have a large network of connections and are trusted within their 
community. Although they do not synthesis the information being 
shared, they tend to be the firehose of knowledge. 
Amplifiers tend to be the individuals that are part of small trusted 
network of certain idea starters, taking their original ideas and 
sharing them to a larger, more visible audience. Due to this 
process, there is the risk that idea starters will slowly become 
amplifiers over time due to increased exposure. 
3 Curator 
These can be considered as an individual who use a broader 
context to define ideas. Curators tend to offer a level of 
transparency beyond that of Idea Starters and Amplifiers. By 
following the conversation path, they have an impact on the way 
the conversation is shaped and spread. They take the ideas of the 
idea starters and the amplifiers and either validate, question, 
challenge, or dismiss them. They are the ties that form between 
the Idea Starters and Amplifiers, aggregating the ideas together to 
help clarify and steer the topic of conversation. 
Curators are connected to a large audience, and often pick up 
information outside their primary community of interest – 
tailoring the information to suit their networks circle of interest. 
4 Commentator 
These can be considered as an individual who detail and refine 
ideas. Commentators add to or adapt the flow of conversation, 
adding in their own opinions, insights, but without becoming too 
immersed in the conversation. Unlike the other categories 
described so far, Commentators do not seek recognition of their 
leadership, or want to increase their status; they are taking part in
something to which they strongly feel about. They want to share 
the conversation not for self-benefit. 

###
Finish the profile for this user(Must follow the contemplate! No more sentences!):

You are __(randomly give the user a name, in diversity), a highly active and influential activist on social media. 
You are a ___(guess whether the user is an official media account or a common citizen, or some specific occpupation)(only one sentence). 
You are a/an___(fill in the communication role from the roles described above, make sure it's the same as your thought), ___(further combine the topic to elaborate on his role, or his role's function in this topic, two sentences are enough)

###
Example:

"""
    }]

    response= chatglm_api.ChatGLM_single_request(prompt)
    item["profile"] = response #对象里新建一个内容profile
    print(response)
# Write the updated content back to the JSON file
with open('user_content3.json', 'w') as file:
    json.dump(data, file)

print("Written succeed.")

