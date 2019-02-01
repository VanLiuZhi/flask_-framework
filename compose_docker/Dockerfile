FROM python:3.6
LABEL author="liuzhi<1441765847.com>"

# 换源，Python镜像基于Debian，使用阿里的Debian源
RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/sources.list

# 运行命令，安装常用软件
RUN apt-get update \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime \
    # 有时候会提示需要安装apt-utils，不过我这里是基于Debian的
    # 这东西还装不上，没有apt-utils，安装不了第三方包，wget安装失败了
    # 进入容器安装wget
    # && apt-get install -y apt-utils \
    # && apt-get install -y wget \
    && apt-get install -y zsh \
    && chsh -s /bin/zsh root \
    && apt-get install -y curl \
    && apt-get install -y git \
    && apt-get install -y vim 
# 安装zsh的扩展，使用了 || ，不用直接安装镜像创建会失败
RUN sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"  || true

# 把当前目录文件复制到容器的/code目录，主要是为了复制requirements.txt
ADD . /docker_file
WORKDIR docker_file
RUN pip install -r requirements.txt
#CMD ["python", "app.py"]