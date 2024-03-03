import requests
import re
import csv
import time
import pandas as pd
 
headers = {
    "Cookie":"appmsglist_action_3274572572=card; RK=XehxU9peSU; ptcz=95a8ffbd10736622148737eb73888f7660e7dddd656271c5870fd813f3651f2c; pac_uid=1_504168539; iip=0; tvfe_boss_uuid=9aee0d93d6d67858; pgv_pvid=5314099328; o_cookie=504168539; pgv_pvi=9233449984; ua_id=mQ5C92HdkxsSpIApAAAAAKZzHtK_BXPTYp3jfSaKY9o=; wxuin=46308164865891; mm_lang=zh_CN; uuid=7a48a466b231ccd67cd8329a06aefb7b; rand_info=CAESIOkdo/sKbVU446lVSmc5E3d9jm+2CB1pJy7mS2lHoveJ; slave_bizuin=3274572572; data_bizuin=3274572572; bizuin=3274572572; data_ticket=a7JfO8AVShaa17EkiagXFtwQDmXXB2H2Ui35fRixQ4ceQq0KbQI3tgjSlE7Gi2yV; slave_sid=UF9XMjJkeXljRGlTMEJtcWpuUFJXOWRLenRVWk1LQ2JqSWxRU0x2dEJEd2tMVVNvUjJwQlpYcENKOE5BS2hlT3J0cHduT2Y1T2tVZ241OWJBSDRJbUpsRUZlNmVMUnAwXzI4MHpiUVpnemNxV0VoNzhVU3dnV3NvRTloeGtHRUxkZDFPRW5YVkd0bEF5RWQ3; slave_user=gh_b77ee583f1f7; xid=56410b97e460e56d19283daf8432f73b",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}
url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
data = {'token':'111525524',           # 隔段时间要更新
       "lang":"zh_CN",
        "f":"json",
        "ajax":"1",
        "action":"list_ex",
        "begin":"0",
        "count":"4",
        "query":"",
        "fakeid":"Mzg2ODU0NTA2Mw==",
        "type":"9",
}
 
content_list = []
n = int(input("需要爬取多少页（一页有四篇）："))
 
for i in range(n):            # 爬取n三页
    data["begin"] = i*4       # 修改data中的begin数值（一页有4个结果）
    time.sleep(3)             # 防止被检测（不要低于3）
 
    content_json = requests.get(url=url,headers=headers,params=data).json()
    # print(content_json) 用于观察
 
    # 获取信息
    breakpoint()
    for item in content_json["app_msg_list"]:
        # 提取每页文章的标题及对应的url
        items = []
        items.append(item["title"])
        items.append(item["link"])
        content_list.append(items)
    print("正在爬取第",i+1,"页")
 
name=['title','link']
test=pd.DataFrame(columns=name,data=content_list)
test.to_csv("test.csv",mode='a',encoding='utf-8')
print("保存成功")
