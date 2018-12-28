FROM ubuntu:18.04

ADD . /sandbox/code/github/threefoldtech/digitalmeX

ENV INSYSTEM=1
env USEGIT=1

RUN apt-get update;apt-get install -y python3.6 curl git locales
RUN mkdir-p /sandbox/code/github/threefoldtech; git clone https://github.com/threefoldtech/jumpscaleX.git /sandbox/code/github/threefoldtech/jumpscaleX
RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py

RUN pip3 install pytest pytest-cov codecov