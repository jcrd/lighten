import dbm.gnu


def to_bytes(v):
    return str(v).encode()


def from_bytes(b):
    return int(b.decode())


class DB:
    def __init__(self, path):
        self.path = path

    def save(self, k, v):
        with dbm.open(self.path, "c") as db:
            db[to_bytes(k)] = to_bytes(v)

    def save_dict(self, d):
        with dbm.open(self.path, "c") as db:
            for k, v in d.items():
                db[to_bytes(k)] = to_bytes(v)

    def get(self, key, max_dev):
        with dbm.open(self.path, "c") as db:
            devs = {}
            k = db.firstkey()
            while k is not None:
                i = from_bytes(k)
                devs[i] = abs(key - i)
                k = db.nextkey(k)
            if len(devs) == 0:
                return None
            devs = sorted(devs.items(), key=lambda i: i[1])
            if devs[0][1] > max_dev:
                return False
            return from_bytes(db[to_bytes(devs[0][0])])
