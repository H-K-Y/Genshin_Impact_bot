from io import BytesIO
import requests
import base64
import json
import time
import os

jsondb_template = {
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


class jsondb:
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding="UTF-8") as f:
                json.dump(jsondb_template, f, ensure_ascii=False, sort_keys=True, indent=4)
        dbfile = open(filepath, "r", encoding="UTF-8")
        self.db = json.loads(dbfile.read())
        self.path = filepath
        dbfile.close()

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
            return user_info(self.db[uid])
        except KeyError:
            self.add_user(uid)
            return user_info(self.db[uid])


class user_info:
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
    jdb = jsondb("t.json")
    user = jdb.user(2632324507)
    print(user.db["time"] == get_time())