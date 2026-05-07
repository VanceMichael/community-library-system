# 跨平台构建的前端 Dockerfile
# 使用多阶段构建：构建阶段和运行阶段

# 构建阶段：使用 Node.js 编译 Vue 应用
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder

WORKDIR /app

# 设置 npm 镜像源，加速构建
RUN npm config set registry https://registry.npmmirror.com

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 构建生产版本
RUN npm run build

# 运行阶段：使用 Nginx 提供静态文件
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# 从构建阶段复制编译后的文件
COPY --from=builder /app/dist .

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 设置时区
ENV TZ=Asia/Shanghai

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
