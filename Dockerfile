FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    mecab-ipadic-utf8 git ca-certificates

ENV HOME /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git $PYENV_ROOT
RUN git clone --depth=1 https://github.com/pyenv/pyenv-virtualenv.git $PYENV_ROOT/plugins/pyenv-virtualenv

RUN pyenv install 3.5.10 && pyenv install 3.6.14 && pyenv install 3.7.11 && pyenv install 3.8.11 && pyenv install 3.9.6 && pyenv install 3.10.1 && pyenv install 3.11.0 && pyenv install 3.12.1

WORKDIR /app
COPY . .
RUN [ "./run-tests.sh", "deploy"]
CMD [ "./run-tests.sh", "test"]
