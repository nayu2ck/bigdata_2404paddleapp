# !/user/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time
import pandas as pd
url = 'http://127.0.0.1:5000/gc'
url1 = 'http://127.0.0.1:5000/gs'
url2 = 'http://127.0.0.1:5000/qgqx'
url3 = 'http://127.0.0.1:5000/pjcq'

text1 = '男，1969年5月出生，汉族，2001年6月加入中国共产党，1992年7月参加工作，东北林业大学铁路与桥梁工程专业毕业，大学学历，硕士学位；1997年03月黑龙江省建设厅住宅与房地产业处科员、副主任科员、主任科员(期间：2002年3月—2005年4月东北林业大学铁路与桥梁工程硕士研究生学习)'
text2 = '广州民航职业技术学院党委副书记、校长，男，1964年9月出生，1985年12月参加工作，1986年7月入党，硕士研究生，西南交通大学交通运输工程专业；'
texts = [text1, text2]
df = pd.read_excel(r"F:\0\0322\paddle\待拆分.xlsx")
texts = (df["最新职务"] + "；" + df["最新学习经历"]).values.tolist()[:16]
df2 = pd.read_excel(r"F:\0\0322\paddle\人物动态.xlsx").dropna(subset=["动态标题", "动态摘要"], how="any")
texts2 = (df2["动态标题"] + "：" + df2["动态摘要"]).values.tolist()[:80]
data = {
        'data': {
            'text': texts,
        },
        'parameters': {
            'getbym': False,
            'dealblend': True,
            'priorlayer': True,
            'schema': []
        }
    }
data1 = {
        'data': {
            'text': texts,
        },
        'parameters': {
            'getbym': False,
            'returnmodelop': False,
            'schema': []
        }
    }
data2 = {
        'data': {
            'text': texts2, # 输入语句组成的列表
        },
        'parameters': {
            'schema': []
        }
    }
# for text in texts[93:]:
#     print(text)
#     data = {
#         'data': {
#             'text': text,
#         },
#         'parameters': {
#             'getbym': False,
#             'schema': []
#         }
#     }
#     t1 = time.time()
#     r = requests.get(url=url, data=json.dumps(data))
#     result_json = json.loads(r.text)
#     print(f"{time.time()-t1:.2f}s")
#     print(json.dumps(result_json, indent=4, ensure_ascii=False))
print('\n'.join(texts2))
r2 = requests.get(url=url2, data=json.dumps(data2))
print(json.dumps(json.loads(r2.text), indent=4, ensure_ascii=False))
r2 = requests.get(url=url3, data=json.dumps(data2))
print(json.dumps(json.loads(r2.text), indent=4, ensure_ascii=False))
print('\n'.join(texts))
t1 = time.time()
r = requests.get(url=url1, data=json.dumps(data1))
result_json = json.loads(r.text)
print(f"{(time.time() - t1) / len(texts):.2f}s")
print(json.dumps(result_json, indent=4, ensure_ascii=False))
t1 = time.time()
r = requests.get(url=url, data=json.dumps(data))
result_json = json.loads(r.text)
print(f"{(time.time() - t1) / len(texts):.2f}s")
print(json.dumps(result_json, indent=4, ensure_ascii=False))
print()