from threading import Thread
from bot import run
from grabbers.pixiv import PixivRecommendedGrab
from filters import TagsFilter

recGrab = PixivRecommendedGrab(filters=[TagsFilter(noTags=["R-18", "3D", "3DCG"])])
ts = [Thread(target=x) for x in (recGrab.run, run)]
[p.start() for p in ts]
[p.join() for p in ts]