from threading import Thread
from time import sleep
from bot import run
import grab
import push

def schedule():
    grab.sc.run_pending()
    push.sc.run_pending()
    sleep(1)

ts = [
    Thread(target=run),
    Thread(target=schedule)
]
[p.start() for p in ts]
[p.join() for p in ts]