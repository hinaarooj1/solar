import asyncio
import datetime

from database import get_database
from repositories import UserRepository
from auth_utils import get_password_hash


USERNAME = "customer1"
PASSWORD = "Passw0rd!"
SECRET = "UserSecret123"
WATCHPOWER_USERNAME = "Ahmarjb"
WATCHPOWER_PASSWORD = "Ahmar123"
SERIAL_NUMBER = "96342404600319"
WIFI_PN = "W0034053928283"
DEV_CODE = 2488
DEV_ADDR = 1
NOTIFICATION_EMAIL = "ahmarjabbar7@gmail.com"


async def main() -> None:
    db = get_database()
    repo = UserRepository(db)

    existing = await repo.get_by_username(USERNAME)
    if existing:
        print("User already exists; skipping creation")
        return

    user_document = {
        "_id": USERNAME,
        "username": USERNAME,
        "password_hash": get_password_hash(PASSWORD),
        "secret": SECRET,
        "watchpower_username": WATCHPOWER_USERNAME,
        "watchpower_password": WATCHPOWER_PASSWORD,
        "watchpower_serial_number": SERIAL_NUMBER,
        "watchpower_wifi_pn": WIFI_PN,
        "watchpower_dev_code": DEV_CODE,
        "watchpower_dev_addr": DEV_ADDR,
        "notification_email": NOTIFICATION_EMAIL,
        "is_active": True,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }

    await repo.create_user(user_document)
    print("User created successfully")


if __name__ == "__main__":
    asyncio.run(main())


