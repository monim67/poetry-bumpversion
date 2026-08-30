FROM python:3.14

RUN pip install "poetry>=2.0"

RUN curl -fsSL https://pyenv.run | bash
ENV PYENV_ROOT="/root/.pyenv" PATH="/root/.pyenv/bin:$PATH:/root/.pyenv/shims"
RUN pyenv install 3.14 3.13 3.10 \
    && pyenv global 3.14 3.13 3.10
