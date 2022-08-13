from utils.pixiv import PixivIllust

REGIONS = ["pixiv"]
TYPES = [PixivIllust]

MAP = {
    k:v for k,v in zip(REGIONS, TYPES)
}