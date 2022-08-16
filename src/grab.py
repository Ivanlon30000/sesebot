from grabbers.pixiv import PixivRecommendedGrab
from filters import TagsFilter
from utils import CONFIG

recGrab = PixivRecommendedGrab(filters=[TagsFilter(noTags=["R-18", "3D", "3DCG"])],
                               expire=CONFIG["expire"])

recGrab.run()