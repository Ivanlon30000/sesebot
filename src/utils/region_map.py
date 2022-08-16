from utils.pixiv import PixivIllust

"""
映射 utils.types.Illust 的 region 对应的类
"""
REGIONS = ["pixiv"]
TYPES = [PixivIllust]

MAP = {
    k:v for k,v in zip(REGIONS, TYPES)
}