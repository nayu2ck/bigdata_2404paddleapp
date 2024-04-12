# !/user/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from paddlenlp import SimpleServer, Taskflow
import threading
import json
import re
from tools import dc_simi, maxprob, joind, nodu, maxl, seg_yr, mod_gender, is_job, MyThread
from bisect import bisect_left

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', egtext = "广州民航职业技术学院党委副书记、校长，男，1964年9月出生，1985年12月参加工作，1986年7月入党，硕士研究生，西南交通大学交通运输工程专业；",exmp1 = [{'学习经历': [{'text': '硕士研究生', 'start': 54, 'end': 59, 'probability': 0.8741765241907302, 'relations': {'高校': [{'text': '西南交通大学', 'start': 60, 'end': 66, 'probability': 0.8877937371188693}], '大学': [{'text': '西南交通大学', 'start': 60, 'end': 66, 'probability': 0.9374215443706575}], '院系': [{'text': '西南交通大学', 'start': 60, 'end': 66, 'probability': 0.30447743659533444}, {'text': '广州民航职业技术学院', 'start': 0, 'end': 10, 'probability': 0.45310883901764853}], '专业': [{'text': '交通运输工程专业', 'start': 66, 'end': 74, 'probability': 0.5421452062498986}], '入学年份': [{'text': '1985年12月', 'start': 31, 'end': 39, 'probability': 0.33945860359601454}]}}], '性别': [{'text': '男', 'start': 19, 'end': 20, 'probability': 0.6321880389188266}], '年龄': [{'text': '1964年9月', 'start': 21, 'end': 28, 'probability': 0.9913217349385803}], '相关高校': [{'text': '西南交通大学', 'start': 60, 'end': 66, 'probability': 0.4889158049026321, 'relations': {'任职': [{'text': '党委副书记', 'start': 10, 'end': 15, 'probability': 0.4328522319179484}]}}]}])#'Hello!\nthis is an application to disaggregate information based on PaddleNLP.'


schema0 = {'学习经历': ['高校', '大学', '学院', '院系', '专业', '入学年份', '毕业年份', '学位', '学历'], "籍贯":['出生地'], "性别":[], "年龄":["出生年"], "工作":["行业", "职务", "单位", "地址"]}
schema2 = {"相关高校":["毕业", "任职", "历任", "曾任"], '政界':['局', '厅', '司'], '商界':['企业']}
tags = ['政界', '商界']
schema0.update(schema2)

schemaz = ['任职情况', '职务', '教育背景']
schemax = ['毕业院校', '专业', '入学年份', '毕业年份', '学位', '学历']
schemac = ['行业', '职务', '单位', '省市']
schemab = ["籍贯", '性别', '年龄']
scheman = {}
provided = {'学习经历': schemax, '工作经历': schemac, '基本信息': schemab}

uie1 = Taskflow("information_extraction", schema=schema0, home_path='./.paddlenlp/')
uie2 = Taskflow("information_extraction", schema=schemaz, home_path='./.paddlenlp/')#device_id=1
# uie2 = None
@app.route('/get',methods=["GET", "POST"])
def getraw():
    global uie1, uie2, schema0, scheman
    if request.method == "GET" or request.method == "POST":
        # 以POST方式传参数，通过form取值
        # 如果Key之不存在，报错KeyError，返回400的页面
        req = json.loads(request.data.decode('gbk'))
        text = req['data']['text']
        schema = req['parameters']['schema'] if 'schema' in req['parameters'] else None
    elif request.method == "POST":
        text = request.form['data']['text']
        schema = request.form['parameters']['schema'] if 'schema' in request.form['parameters'] else None
    if schema:
        scheman = schema
        uie1.set_schema(schema)# = Taskflow("information_extraction", schema=schema, device_id=0)
    else:
        scheman = {}
        uie1.set_schema(schema0)
    # if type(text) is list:
    #     res = [uie1(x) for x in text]
    #     return res
    return uie1(text)


@app.route('/gs',methods=["GET", "POST"])
def getquarter():
    if request.method == "GET" or request.method == "POST":
        # 以POST方式传参数，通过form取值
        # 如果Key之不存在，报错KeyError，返回400的页面
        req = json.loads(request.data.decode('gbk'))
        text = req['data']['text']
        schema = req['parameters']['schema'] if 'schema' in req['parameters'] else None
        month = req['parameters']['getbym'] if 'parameters'in req and 'getbym' in req['parameters'] else True
        imed = req['parameters'].get('returnmodelop', False)
    elif request.method == "POST":
        text = request.form['data']['text']
        schema = request.form['parameters']['schema'] if 'schema' in request.form['parameters'] else None
        month = request.form['parameters']['getbym'] if 'parameters' in request.form and 'getbym' in request.form['parameters'] else True
        imed = request.form['parameters'].get('returnmodelop', False)
    schema = provided[schema] if type(schema) is str else (schema if schema else schemab + schemac + schemax)
    uie2.set_schema(schema)
    ans_ = uie2(text)
    if imed:
        return ans_
    results = []
    for ans in ans_:
        result = {}
        for k in schema:
            v = maxprob(ans[k])['text'] if k in ans else ""
            v = mod_gender(v) if k == '性别' else v
            result[k.replace('省市', '地址') if k != '年龄' else ('出生年月' if month else '出生年')] = seg_yr(v) if (k == '年龄' and not month) else v
        results.append(result)
    return results


def 拆分经历(x, text, pt="；，。"):
    do_punc = lambda x: [-1] + [i.start() for i in re.finditer(f'[{pt}]', text[x])]
    puncs = do_punc(x)
    if puncs[-1] < len(text[x]) - 1:
        puncs.append(len(text[x]))
    return puncs


def 经历分段(text):
    puncs_list = list(map(lambda x: 拆分经历(x, text), range(len(text))))
    uie2.set_schema(schemaz)
    分段s = uie2(text)
    关键词位置s = {"学习经历": list(zip([min([999] + [y['start'] for y in x.get('教育背景', "")]) for x in 分段s],
                                        [min([999] + [y['end'] for y in x.get('教育背景', "")]) for x in 分段s])),
                 "工作经历": list(zip([min([999] + [y['start'] for y in x.get('职务', []) + x.get('任职情况', [])]) for x in
                            分段s], [min([999] + [y['end'] for y in x.get('职务', []) + x.get('任职情况', [])]) for x in 分段s]))}
    getxx = lambda u: text[u][
                      puncs_list[u][bisect_left(puncs_list[u], 关键词位置s['学习经历'][u][0]) - 1] + 1:puncs_list[u][
                          bisect_left(puncs_list[u], 关键词位置s['学习经历'][u][1])]] if 关键词位置s['学习经历'][u][
                                                                                             0] < 999 else ""
    getgz = lambda u: text[u][
                      puncs_list[u][bisect_left(puncs_list[u], 关键词位置s['工作经历'][u][0]) - 1] + 1:puncs_list[u][
                          bisect_left(puncs_list[u], 关键词位置s['工作经历'][u][1])]] if 关键词位置s['工作经历'][u][
                                                                                             0] < 999 else ""
    text工作s = [getgz(i) for i in range(len(text))]
    text学习s = [getxx(i) for i in range(len(text))]
    uie2.set_schema(schemac)
    ans_gz = uie2(text工作s)
    uie2.set_schema(schemax)
    ans_xx = uie2(text学习s)

    result_x = []
    result_g = []
    for i in range(len(text)):
        result_x.append({})
        result_g.append({})
        for k in schemax:
            v = maxprob(ans_xx[i][k])['text'] if k in ans_xx[i] else ""
            if v:
                result_x[i][k] = v
        for k in schemac:
            v = maxprob(ans_gz[i][k])['text'] if k in ans_gz[i] else ""
            if v:
                result_g[i][k] = v

    return {"工作经历": result_g, "学习经历": result_x}


@app.route('/gc',methods=["GET", "POST"])
def getmed():
    global uie1, uie2, schema0, scheman
    if request.method == "GET" or request.method == "POST":
        req = json.loads(request.data.decode('gbk'))
        text = req['data']['text']
        month = req['parameters']['getbym'] if 'parameters'in req and 'getbym' in req['parameters'] else True
        su = req['parameters'].get('dealblend', False)
        layup = req['parameters'].get('priorlayer', False)
    elif request.method == "POST":
        text = request.form['data']['text']
        month = request.form['parameters']['getbym'] if 'parameters' in request.form and 'getbym' in request.form['parameters'] else True
        su = request.form['parameters'].get('dealblend', False)
        layup = request.form['parameters'].get('priorlayer', False)

    if su:
        t_pre = MyThread(经历分段, (text,))
        t_pre.start()

    if scheman:
        uie1.set_schema(schema0)
    results = []
    ans_ = uie1(text)
    for ans in ans_:
        result = {}
        if '学习经历' in ans:
            xjs = ans['学习经历']
            xjs = [maxprob(xjs)] if dc_simi([x['text'] for x in xjs]) else xjs
            result['学习经历'] = []
            for xj in xjs:
                exp = {}
                rl = xj['relations'] if 'relations' in xj else {}
                xj = xj['text']
                xxs = ['学习经历', '高校', '大学', '学院', '院系']
                xxs = list(filter(lambda x: x in rl, xxs))
                xxs = list(map(lambda x: rl[x], xxs))
                unis = [[x['text'] for x in y] for y in xxs]
                unis = nodu([element for sublist in unis for element in sublist])
                schools = list(filter(lambda x: x and ('学院' in x or x[-1] in ["院", "系"]), unis))
                unis = [x for x in unis if x not in schools]
                exp.update({"学校": maxl(unis), "院系":maxl(schools)})
                for fld in ['专业', '入学年份', '毕业年份']:
                    subj = rl[fld] if fld in rl else []
                    exp[fld] = maxprob(subj)['text'] if subj else ""
                xls = ["学位", "学历"]
                xls = list(filter(lambda x: x in rl, xls))
                xls = list(map(lambda x: rl[x], xls))
                xls = maxprob([x for y in xls for x in y])['text'] if xls else ""
                exp["学历"] = xls if xls else xj
                result['学习经历'].append(exp)
        for k in ['籍贯', '性别', '年龄']:
            v = maxprob(ans[k])['text'] if k in ans else ""
            v = mod_gender(v) if k == '性别' else v
            result[k if k != '年龄' else ('出生年月' if month else '出生年')] = seg_yr(v) if (k == '年龄' and not month) else v
        if '工作' in ans:
            for k in ["行业", "职务", "单位", "地址"]:
                v = maxprob([maxprob(x['relations'][k]) for x in ans['工作'] if 'relations' in x and k in x['relations']])
                result[k] = v['text'] if v else (joind([x['text'] for x in ans['工作'] if is_job(x['text'])]) if k=="职务" else "")
        if '相关高校' in ans:
            rluns = [max(ans['相关高校'], key=lambda x: x['probability'])] if dc_simi([x['text'] for x in ans['相关高校']]) else ans['相关高校']
            for rlun in rluns:
                if 'relations' in rlun:
                    for k in rlun['relations'].keys():
                        if min([x['start'] for x in rlun['relations'][k]]) in range(rlun['end'], rlun['end'] + 5):
                            result[k.replace("历", "曾").replace("学习", "毕业")+"高校"] = {rlun['text']: joind([x['text'] for x in rlun['relations'][k]])}
                        elif '学习经历' not in result:
                            result['毕业高校'] = rlun['text']
        if [x for x in tags if x in ans]:
            result['标签'] = []
            for tag in tags:
                if tag in ans:
                    print(ans[tag])
                    result['标签'].append(tag)
        results.append(result)
    if su:
        t_pre.join()
        results2 = t_pre.get_result()
        for i in range(len(results)):
            for k in results2["学习经历"][i]:
                if '学习经历' not in results[i] or not results[i]["学习经历"][0].get(k.replace("学位", "学历").replace('毕业院校', '学校'), not layup):
                    v = results2["学习经历"][i][k]
                    if '学习经历' not in results[i]:
                        results[i]["学习经历"] = [{"学校":"", "院系":"", "专业":"", "毕业年份":"", "入学年份":"", "学历":""}]
                    results[i]["学习经历"][0][k.replace("学位", "学历").replace('毕业院校', '学校')] = v
                    print(v)
            for k in results2["工作经历"][i]:
                if not results[i].get(k.replace("省市", "地址")) or layup:
                    v = results2["工作经历"][i][k]
                    results[i][k.replace("省市", "地址")] = v
                    print(v)
    return results

@app.route('/qgqx',methods=["GET", "POST"])
def getemo():
    schemad = '情感倾向[正向，负向]'  # 分类任务需要[]来设置分类的label
    if request.method == "GET" or request.method == "POST":
        req = json.loads(request.data.decode('gbk'))
        text = req['data']['text']
        schema = req['parameters']['schema'] if 'schema' in req['parameters'] else None
    elif request.method == "POST":
        text = request.form['data']['text']
        schema = request.form['parameters']['schema'] if 'schema' in request.form['parameters'] else None
    uie2.set_schema(schema if schema else schemad)
    return uie2(text)

@app.route('/pjcq',methods=["GET", "POST"])
def getcom():
    schemad = {'评价维度': ['观点词', '情感倾向[正向，负向]']}  # 分类任务需要[]来设置分类的label
    if request.method == "GET" or request.method == "POST":
        req = json.loads(request.data.decode('gbk'))
        text = req['data']['text']
        schema = req['parameters']['schema'] if 'schema' in req['parameters'] else None
    elif request.method == "POST":
        text = request.form['data']['text']
        schema = request.form['parameters']['schema'] if 'schema' in request.form['parameters'] else None
    uie2.set_schema(schema if schema else schemad)
    return uie2(text)

# app = SimpleServer()
# app.register_taskflow('taskflow/uie', [uie1, uie2])
if __name__ == '__main__':
    # t = threading.Thread(target=worker)
    # t.daemon = True
    # t.start()
    # 已经把端口改成80

    app.run(port=5000, host='0.0.0.0')#, threaded=True)