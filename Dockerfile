FROM python:3.8

# RUN [ "apk", "add", "--no-cache", "--update", "--virtual", ".build-deps", "gcc", "py3-cryptography", "py3-numpy", "py3-pandas", "py3-cairo", "musl-dev" ]
RUN ["apt-get", "update", "-y"]
RUN ["apt-get", "install", "-y", "libgirepository1.0-dev", "gcc", "libcairo2-dev", "pkg-config", "gir1.2-gtk-3.0", "ffmpeg"]

COPY . /app

WORKDIR /app

RUN [ "pip", "install", "-r", "requirements.txt" ]

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT [ "python", "/app/main.py" ]