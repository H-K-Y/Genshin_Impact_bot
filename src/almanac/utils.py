import base64
import json
import uuid
import time
from pathlib import Path
from io import BytesIO

TEMPLATE = {
    "10001": {
        "time": "2021-06-04",
        "pos": "二八"
    }
}


def text_r90(t):
    tmp = ""
    for char in t:
        tmp += f"{char}\n"
    return tmp


class SimpleJsonDB:
    def _load(self):
        with open(self.path, 'r', encoding='utf8') as json_file:
            self._database = json.load(json_file)

    def find(self, filters: dict):
        for k, v in filters.items():
            for _ in self._database:


    def __init__(self, db_path: Path):
        if not isinstance(db_path, Path):
            db_path = Path(db_path)
        if not db_path.exists():
            with open(db_path, 'w', encoding="UTF-8") as f:
                json.dump(TEMPLATE, f, ensure_ascii=False, sort_keys=True, indent=4)
        self.path = db_path
        self._database = [
            {
                "_id": "uuid4-uuid4-uuid4-uuid4",
                "uid": 10001,
                "time": "2023-02-10"
            }
        ]

    def add_user(self, uid):
        uid = str(uid)
        self.db[uid] = {
            "time": "",
            "pos": ""
        }

    def del_user(self, uid):
        uid = str(uid)
        del self.db[uid]

    def user_list(self):
        return list(self.db.keys())

    def save(self):
        with open(self.path, 'w+', encoding="UTF-8") as f:
            json.dump(self.db, f, ensure_ascii=False, sort_keys=True, indent=4)

    def user(self, uid):
        uid = str(uid)
        try:
            return UserInfo(self.db[uid])
        except KeyError:
            self.add_user(uid)
            return UserInfo(self.db[uid])


class UserInfo:
    def __init__(self, db):
        self.db = db
        self.time = db["time"]
        self.pos = db["pos"]

    def write(self, pos):
        self.db["pos"] = pos
        self.db["time"] = time.strftime("%Y-%m-%d")


def get_cq(imp):
    bio = BytesIO()
    imp.save(bio, format='PNG')
    base64_str = base64.b64encode(bio.getvalue()).decode()
    pic_b64 = f'base64://{base64_str}'
    return f'[CQ:image,file={pic_b64}]'


def get_time():
    return time.strftime("%Y-%m-%d")


if __name__ == "__main__":
    jdb = SimpleJsonDB("t.json")
    user = jdb.user(2632324507)
    print(user.db["time"] == get_time())
