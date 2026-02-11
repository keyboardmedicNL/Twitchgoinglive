FROM alpine:latest

# The installer requires curl (and certificates) to download the release archive
RUN apk update && apk add curl ca-certificates python3

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /usr/src/app

COPY . .

RUN uv sync

CMD [ "uv", "run" "src/going_live.py" ]