from grabbers.pixiv import PixivRecommendedGrab
from filters import TagsFilter

recGrab = PixivRecommendedGrab(filters=[TagsFilter(noTags=["R-18", "3D", "3DCG"])])

recGrab.run()