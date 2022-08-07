from threading import Thread

if __name__ == "__main__":
    import grab
    import push
    import botloop
    
    ts = [Thread(target=x.main) for x in (grab, push, botloop)]
    [p.start() for p in ts]
    [p.join() for p in ts]
