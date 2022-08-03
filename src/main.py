from multiprocessing import Process

if __name__ == "__main__":
    from picture_grab import run
    from bot import bot
    processes = []
    pix = Process(target=run)
    botp = Process(target=bot.infinity_polling, kwargs={"skip_pending": True})
    processes.append(pix)
    processes.append(botp)
    [p.start() for p in processes]
    [p.join() for p in processes]