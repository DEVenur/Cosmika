FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Cache dependencies separately from source changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# Store example configs at a path not shadowed by the config volume mount
RUN mkdir -p /app/config.examples && \
    cp /app/config/runtime.yml.example /app/config.examples/ && \
    cp /app/config/chat_sys_prompt.txt.example /app/config.examples/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
