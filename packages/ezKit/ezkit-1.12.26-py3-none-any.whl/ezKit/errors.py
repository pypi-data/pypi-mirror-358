# 内部错误: 1000
internal_error = {
    "type": {
        "code": 1001,
        "message": "type error",
    },
}

# HTTP错误: 2000
http_error = {
    "request_data": {
        "code": 2001,
        "message": "HTTP request data error",
    },
}

# 数据库错误: 3000
database_error = {
    "create": {
        "code": 3001,
        "message": "Database create data error",
    },
    "read": {
        "code": 3002,
        "message": "Database read data error",
    },
    "update": {
        "code": 3003,
        "message": "Database create data error",
    },
    "delete": {
        "code": 3004,
        "message": "Database delete data error",
    },
    "build_sqlalchemy_where": {
        "code": 3005,
        "message": "Database build SQLAlchemy WHERE error",
    },
}
