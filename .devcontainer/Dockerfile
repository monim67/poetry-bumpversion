FROM python:3.12

RUN pip install "poetry>=1.2"

RUN curl -fsSL https://pyenv.run | bash
ENV PYENV_ROOT="/root/.pyenv" PATH="/root/.pyenv/bin:$PATH:/root/.pyenv/shims"
RUN pyenv install 3.10 3.9 \
    && pyenv global 3.10 3.9
