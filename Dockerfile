# 使用Python作为基础镜像
FROM python:3.8
# 设置工作目录
WORKDIR /paddleapp
# 复制应用代码到容器中
COPY requirements.txt ./
COPY . .
# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 暴露应用端口
EXPOSE 5000
# 设置启动命令
CMD ["python", "chaifenapp.py"]