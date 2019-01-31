# flask_framework

通用的flask框架，整合常用技术服务，快速构建原型

## 技术栈

1. 数据库
    1. MySQL(主数据库)，使用SQLALchemy
    2. Redis(缓存，副数据库)
    3. MongoDB(副数据库)，使用MongoEngine

2. 任务队列
    1. Celery
    2. RabbitMQ
    3. Redis
    
3. 搜索服务
    Elasticsearch
    
4. 容器技术 Docker
    1. docker-compose
    2. Dockerfile

## 架构

### 应用

1. 模型
    1. User 用户
    2. Contact 
    3. Post 
    4. Comment 评论
    5. Like 点赞
    6. Collect 收藏
    7. Tag 标签


### 启动文件

1. 配置文件和本地配置文件
2. docker-compose配置文件以及相关文件（存放在docker_compose_config文件夹中）
    
### 创建数据库

1. flask db init
2. flask db migrate
3. flask db upgrade