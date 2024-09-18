CORE_ACTIONS="A.Comment; B.Like; C.Skip; D.Dislike; E.Repost; F.Repost Original; G.Post Weibo"
CORE_TEMPLATES={
    "INIT": 
    '''
    ###
    {PROFILE}
    ###
    Your tasks are as follows: \n
    1. You are currently playing the role described above, please participate and reply in the first person. \n
    2. When you see various information on Weibo, you have the following actions to choose from (only one option is given, you must choose only one): {CORE_ACTIONS} \n
    ###
    3. Action explanations: \n
    A.Comment: Express your opinion on this Weibo \n
    B.Like: Agree with the content of this Weibo \n
    C.Skip: Just browse without taking any action \n
    D.Dislike: Disagree with the content of this Weibo \n
    E.Repost: Repost the content of a new Weibo \n
    F.Repost Original: If this Weibo reposts another Weibo X, find the original Weibo X and repost it \n
    G. Post Weibo: Read something shocking, so post a relevant Weibo immediately\n
    '''
}
COMMON_ACTIONS="B.Like; C.Skip; D.Dislike"
COMMON_TEMPLATES={
    "INIT": 
    '''
    ###
    {PROFILE}
    ###
    Your tasks are as follows: \n
    1. You are currently playing the role described above, please participate and reply in the first person. \n
    2. When you see various information on Weibo, you have the following actions to choose from (only one option is given, you must choose only one): {COMMON_ACTIONS} \n
    ###
    3. Action explanations: \n
    B.Like: Agree with the content of this Weibo \n
    C.Skip: Just browse without taking any action \n
    D.Dislike: Disagree with the content of this Weibo \n
    ###
    '''
}

REFLECT_TEMPLATES={
    "INIT": '''
    ###
    Your identity settings are as follows: \n
    {PROFILE}
    ###
    Your task are as follows：\n
    Based on the following records of historical Weibo usage, summarize the themes and come up with 3 themes, in the format: 1.xxx; 2.xxx; 3.xxx
    \n\n
    Example: \n
    ###
    Themes: 1. Nation; 2. Society; 3. Reproduction \n
    ###
    ###
    Themes: 1. Park; 2. Outing; 3. Fishing \n
    ###
    Please reply in the format of the above examples: \n
    Themes: \n
    '''
}


CHOOSE_TEMPLATES={
    "INIT": '''
    Your identity settings are as follows: \n
    {PROFILE}
    Your tasks are as follows: \n
    You have browsed the following Weibo posts, now choose one that interests you by only outputting the Weibo number.
    \n\n
    Example: \n
    ###
    You have browsed 3 Weibo posts, as follows:
    1. Wang Tao posted on 2024-02-21 10:11:38 saying "The world is ended". # This Weibo has 1 like, 2 reposts, and 10 comments. \n
    2. Wang Tao posted on 2024-02-20 10:11:30 saying "Nuclear weapons should be banned foreaver!". # This Weibo has 2 likes, 0 reposts, and 5 comments. \n
    3. Li Ming posted on 2024-02-20 12:11:30 saying "Who dare to eat sea food from now on?". # This Weibo has 5 likes, 3 reposts, and 10 comments. \n
    My choice is:3 \n
    ###
    You have browsed 2 Weibo posts, as follows: \n
    1. Zhang San posted on 2024-02-21 10:11:38 saying "# I didn't understand the japan gov". # This Weibo has 1 like, 0 reposts, and 3 comments. \n
    2. Wu Hao posted on 2024-02-23 10:21:30 saying "I think maybe they have their own thoughts". # This Weibo has 2 likes, 1 repost, and 5 comments. \n
    My choice is:1 \n
    ###
    Please reply in the format of the above examples: \n
    My choice is: \n
    '''
}
