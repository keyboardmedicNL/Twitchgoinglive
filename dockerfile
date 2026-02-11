FROM ghcr.io/astral-sh/uv:latest

WORKDIR /usr/src/app

COPY . .

CMD [ "uv", "run" "src/going_live.py" ]