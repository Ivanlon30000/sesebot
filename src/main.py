from multiprocessing import Process

if __name__ == "__main__":
    import grab
    import push
    
    processes = [Process(target=x.main) for x in (grab, push)]
    [p.start() for p in processes]
    [p.join() for p in processes]
