# 跨平台构建的后端 Dockerfile
# 基础镜像：Python 3.11 slim 版本，支持 ARM 和 X86 架构

FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=library_system.settings
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "library_system.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
