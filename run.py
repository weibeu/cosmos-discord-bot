from cosmos.core.cosmos import Cosmos

if __name__ == "__main__":
    bot = Cosmos()
    print(f"All initial tasks completed. [{round(bot.time.time(), 3)} seconds.]")
    bot.run()
