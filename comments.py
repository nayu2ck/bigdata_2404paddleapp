# !/user/bin/env python3
# -*- coding: utf-8 -*-
import paddle
from paddlenlp.transformers import SkepTokenizer, SkepModel
from utils import data_ext, data_cls
from utils.utils import decoding, concate_aspect_and_opinion, format_print
# 映射表
label_ext_path = "/home/aistudio/work/label_ext.dict"
label_cls_path = "/home/aistudio/work/label_cls.dict"

# PaddleNLP开源的基于全量数据训练好的评论观点抽取模型和属性级情感分类模型
ext_model_path = "/home/aistudio/data/best_ext.pdparams"
cls_model_path = "/home/aistudio/data/best_cls.pdparams"

# load dict
model_name = "skep_ernie_1.0_large_ch"
ext_label2id, ext_id2label = data_ext.load_dict(label_ext_path)
cls_label2id, cls_id2label = data_cls.load_dict(label_cls_path)
tokenizer = SkepTokenizer.from_pretrained(model_name)
print("label dict loaded.")

# load ext model   加载观点抽取模型
ext_state_dict = paddle.load(ext_model_path)
ext_skep = SkepModel.from_pretrained(model_name)
ext_model = SkepForTokenClassification(ext_skep, num_classes=len(ext_label2id))
ext_model.load_dict(ext_state_dict)
print("extraction model loaded.")

# load cls model   加载属性级情感分析模型
cls_state_dict = paddle.load(cls_model_path)
cls_skep = SkepModel.from_pretrained(model_name)
cls_model = SkepForSequenceClassification(cls_skep, num_classes=len(cls_label2id))
cls_model.load_dict(cls_state_dict)
print("classification model loaded.")