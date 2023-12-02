FROM python:3.10.13-slim-bullseye

WORKDIR /app

COPY . /app

# 指定源, 如果后期源挂了, 更换个源就可以.
RUN pip install --no-cache -i https://pypi.mirrors.ustc.edu.cn/simple/  -r requirements.txt

CMD [ "python", "main.py" ]