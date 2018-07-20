* 配置文件在 instance/config
* 入口文件 run.py
* 接口文档在 /api/v1
* 先创建数据库,再调用初始化接口
* 初始化接口 /api/v1/tools/init_database/
```
.
├── app#项目根目录
│   ├── __init__.py#app包初始化文件
│   ├── ext#插件包
│   │   ├── cache.py#缓存插件
│   │   ├── csrf.py#csrf保护
│   │   ├── db.py#数据库
│   │   ├── __init__.py#插件包初始化文件
│   │   └── logger.py#日志
│   ├── models #模型包,保存所有数据库模型,供sqlalchemy使用
│   │   └──__init__.py
│   ├── utils #一些工具,下面都是工具,目录只是为了分类
│   │   ├── auth 
│   │   │   ├── auth.py
│   │   │   ├── __init__.py
│   │   │   └── jwt.py
│   │   ├── __init__.py
│   │   └── tools
│   │       ├── ContextualFilter.py
│   │       └── __init__.py
│   └── views #视图包
│       ├── api_v1 #Api视图包
│       │   ├── __init__.py#Api包初始化文件,里面实例化了一个Flask-restplus的Api类,并注册到api蓝图,而且把所属namespace注册到api
│       │   ├── facilities
│       │   │   └──  __init__.py
│       │   ├── gateways
│       │   │   ├── gateway.py
│       │   │   └── __init__.py
│       │   ├── homes
│       │   │   └── __init__.py
│       │   ├── institutes
│       │   │   └── __init__.py
│       │   ├── sensors
│       │   │   └── __init__.py
│       │   ├── tools
│       │   │   ├── database.py
│       │   │   └── __init__.py
│       │   └── users #User NameSpace
│       │       ├── __init__.py# 包初始化文件,里面定义本空间的一些api
│       │       ├── models.py #里面存放输出参数序列化model
│       │       └── parsers.py #里面存储入参控制
│       └── __init__.py #视图初始化文件,里面定义了api的蓝图,并引用了api_v1包
├── docker-compose.yml #docke-compose部署文件
├── Dockerfile #Docker构建文件
├── instance #配置包
│   ├── config.py #配置文件
│   ├── __init__.py
│   ├── jwt_rsa_private_key.pem
│   └── jwt_rsa_public_key.pem
├── README.md
├── requirement.txt #项目依赖
└── run.py #入口文件
```
