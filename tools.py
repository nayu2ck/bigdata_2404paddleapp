# !/user/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import threading
import time

import pandas as pd
import os

job_list = ['市长', '书记', '秘书', '区长', '主任', '常委', '部长', '主席', '成员', '党委', '政府', '人大', '政协', '干部'] #干部
job_list += ['局长', '司长', '院长', '副局长', '工程师', '调研员', '调查员', '组长', '党组成员', '处长', '总工', '经理', '党组成员', '总监', '主任', '巡视员', '厅长', '会计师', '经理', '指挥', '站长', '总裁', '董事']  # edit 更新 4.10
specialization_list = ['分工', '工作', '负责', '主管', '职责', '分管', '主持', '协调', '协助', '联系', '指导', '履行', '参与', '个人简历'] #更新 3.8

def spillt(t: str, s):
    try:
        if type(t)==list:
            r = []
            for tt in t:
                if '.' in tt[1:][:-1]:
                    if str.isdigit(tt[tt.index('.')-1]) and str.isdigit(tt[tt.index('.')+1]):
                        r.append(s)
                        continue
                r += tt.split(s)
            return r
        for sp in s:
            t = spillt([t] if type(t)==str else t, sp)
        while type(t) == list and '' in t:  # refs == ['']
            t.remove('')
        return t if type(t)==list else [t]
    except:
        print('False Value ', t)
        return t


def yx(s: set, yl):
    l = list(s)
    l.sort(key=lambda x: yl.index(x))
    return l


def is_school(t):
    if pd.isna(t):
        return False
    if is_otype(t):
        return True
    return re.search('大学|学院|[医科信南北工][大]', t) is not None


def is_otype(t):
    if pd.isna(t):
        return False
    return re.search('医院|委员|学会|会议|歌手|导演|演员|作家|画家|中心|政府|市政|党组|常委', t) is not None

def qf(x):
    return not x


def reach_files(pth, topdown=True):
    if not os.path.isdir(pth):
        print('不存在目录')
        return []
    for root, dirs, files in os.walk(pth, topdown):
        if len(files) > 0:
            break
    return files


def splitrows(df, splits=10):
    pis = df.股票代码.apply(lambda x: len(x.split("|")))
    maxam = pis[pis < splits].max()
    for i in range(1, maxam + 1):
        df[f"股票代码_{i}"] = df.股票代码.apply(
            lambda x: yx(set(x.split("|")), x.split("|"))[i - 1] if len(x.split("|")) >= i else "")
    l = [df.loc[df.股票代码.apply(lambda x: "|" not in x)]]
    for i in range(1, maxam + 1):
        odf = df.loc[df.股票代码.apply(lambda x: "|" in x)]
        odf = odf.loc[odf[f"股票代码_{i}"].apply(lambda x: type(x) is str and len(x) > 1)]
        l.append(
            odf[yx(set(odf.columns) - {f"股票代码_{i1}" for i1 in range(1, maxam + 1) if i1 != i}, list(odf.columns))])
    return pd.concat(l).sort_values(by=["单位", "姓名"])


def splitrowsto1col(df, splits=10):
    pis = df.股票代码.apply(lambda x: len(x.split("|")))
    maxam = pis[pis < splits].max()
    for i in range(1, maxam + 1):
        df[f"股票代码_{i}"] = df.股票代码.apply(
            lambda x: yx(set(x.split("|")), x.split("|"))[i - 1] if len(x.split("|")) >= i else "")
    l = [df.loc[df.股票代码.apply(lambda x: "|" not in x)]]
    for i in range(1, maxam + 1):
        odf = df.loc[df.股票代码.apply(lambda x: "|" in x)]
        odf = odf.loc[odf[f"股票代码_{i}"].apply(lambda x: type(x) is str and len(x) > 1)]
        odf.股票代码 = odf[f"股票代码_{i}"]
        l.append(
            odf[yx(set(odf.columns) - {f"股票代码_{i1}" for i1 in range(1, maxam + 1) if i1 != i}, list(odf.columns))])

    return pd.concat(l)[df.columns].sort_values(by=["单位", "姓名"])

def dc_simi(l):
    return len([x for x in l if [y for y in l if x in y and x !=y]]) > 0




def maxprob(l, default=""):
    """
    paddlenlp
    :param l:
    :return:
    """
    return max(l, key=lambda x: x['probability']) if l else default


def maxl(l):
    """
    返回长度最大的字符串
    :param l:
    :return:
    """
    return max(l, key=len) if l else ""

def joind(l, sep="、"):
    """
    分隔符连接成字符串
    :param l:
    :param sep:
    :return:
    """
    return sep.join(l)

def nodu(l):
    return list(set(l))

def seg_yr(t):
    y = re.search('[\d]{1,4}[年|-|.]', t)
    if y:
        return int(y.group()[:-1])
    return t

def mod_gender(t):
    return {"先生": "男", "女士": "女"}.pop(t, t)

def is_job(a, loose=False):  #edit loose
    for job in job_list:
        if job in a:
            return True
    if loose:
        if len(set(a) & set('总委员会局组副主任编辑院长书处工记')) > len(a)/2:
            return True
    return False


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        time.sleep(2)
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None


def wash(t, s):
    return '，'.join(spillt(t, s))


def meval(o):
    if type(o) is not str:
        return o
    try:
        return eval(o)
    except:
        try:
            return json.loads(o)
        except:
            return o


def replall(t, sp, tg):
    for s in sp:
        t = t.replace(s, tg)
    return t


def spread(l, sp="\n"):
    l = [x if len(x) > 0 else "0" for x in l]
    res = (sp if sp else '\n').join(l).split(sp if sp else "\n")
    res = [x if x != "0" else "" for x in res]
    return res


def sticktog(A):
    """
    数组并集
    """
    assert type(A) is list
    if len(A) == 0:
        return [(999,)]
    res = [(A[0]["start"], A[0]["end"])]
    i = 0
    while i < len(A) - 1:
        j = i + 1
        l = min(A[i]["start"], A[j]["start"])
        r = max(A[i]["end"], A[j]["end"])
        if A[j]["start"] <= A[i]["end"] + 1:
            res = res[:-1]
            res.append((l, r))
        else:
            res.append((A[j]["start"], A[j]["end"]))
        i += 1

    return res

def sortlist(l, k):
    l.sort(key=lambda x: x[k])
    return l


def orgnize_rslt(l, default={}):
    """
    maxprob or joind judging by dc_simi
    :param l:
    :return:
    """
    if dc_simi([x.get("text", "") for x in l]):
        return maxprob(l, default).get("text", "")
    else:
        return joind([x.get("text", "") for x in l])