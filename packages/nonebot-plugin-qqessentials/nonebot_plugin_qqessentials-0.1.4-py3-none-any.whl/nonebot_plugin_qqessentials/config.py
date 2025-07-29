from pydantic import BaseModel
from typing import List



class Config(BaseModel):
    """Plugin Config Here"""

    # 数据存储位置
    data_path: str = "./data"
    
    # 头像上传超时时间（秒）
    avatar_upload_timeout: int = 30
    
    # 默认点赞次数，SVIP可考虑修改到20次
    default_like_times: int = 10
    
    # 删除好友功能开关（默认关闭，安全考虑）
    # 环境变量：ENABLE_DELETE_FRIEND
    enable_delete_friend: bool = False
    
    # 加群请求信息推送开关（默认关闭）
    # 环境变量：ENABLE_GROUP_REQUEST_NOTIFY
    enable_group_request_notify: bool = False
    
    # 加群请求推送目标群号列表（只有这些群的加群请求会推送到对应群）
    # 环境变量：GROUP_REQUEST_NOTIFY_TARGET（多个群号用逗号分隔，如：123456789,987654321）
    group_request_notify_target: List[int] = []
    
    # === 随机禁言功能配置 ===
    
    # 随机禁言功能开关（默认开启）
    # 环境变量：ENABLE_RANDOM_BAN
    enable_random_ban: bool = True
    
    # 随机口球/我要口球的时间范围（格式："最小时间-最大时间"，单位：秒，示例："5-60"）
    # 环境变量：RANDOM_BAN_TIME_RANGE
    random_ban_time_range: str = "5-60"
    
    # 禅定/精致睡眠的禁言时间（秒，默认36000秒=10小时）
    # 环境变量：LONG_BAN_TIME
    long_ban_time: int = 36000
    
    # === 词库功能配置 ===
    
    # 词条添加等待超时时间（秒，默认60秒）
    # 环境变量：LEXICON_TIMEOUT
    lexicon_timeout: int = 60
