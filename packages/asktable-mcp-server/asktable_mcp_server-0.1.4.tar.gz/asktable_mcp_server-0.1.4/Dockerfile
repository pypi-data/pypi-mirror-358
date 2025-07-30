FROM python:3.11-slim

WORKDIR /app

# 安装 pip 和 asktable-mcp-server
RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir asktable-mcp-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 暴露默认端口（SSE 模式）
EXPOSE 9000

# 设置容器启动时执行的命令
CMD ["python", "-m", "asktable_mcp_server.sse_server"]