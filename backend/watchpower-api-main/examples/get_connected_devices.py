import os

from dotenv import load_dotenv
from watchpower_api import WatchPowerAPI

load_dotenv()
USERNAMES = os.environ["USERNAMES"]
PASSWORD = os.environ["PASSWORD"]


def main():
    api = WatchPowerAPI()
    api.login(USERNAMES, PASSWORD)
    devices = api.get_devices()

    for device in devices:
        print(device)


if __name__ == "__main__":
    main()
