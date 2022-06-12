import dbm.gnu
import sys
from datetime import datetime, time


def to_bytes(v):
    return bytes(str(v), sys.stdout.encoding)


def from_bytes(b):
    return str(b, sys.stdout.encoding)


class Timestamp:
    FORMAT = "%H%M%S"

    @classmethod
    def from_bytes(cls, b):
        return cls(datetime.strptime(from_bytes(b), cls.FORMAT).time())

    def __init__(self, now=None):
        if not now:
            now = datetime.now().time()
        self.now = now

    def __bytes__(self):
        return to_bytes(self.now.strftime(Timestamp.FORMAT))

    def midday(self):
        return Timestamp(time(12)).total_seconds()

    def midnight(self):
        return Timestamp(time(23, 59, 59)).total_seconds()

    def total_seconds(self):
        n = self.now
        return n.hour * 60 * 60 + n.minute * 60 + n.second

    def distance(self):
        s = self.total_seconds()
        if s > self.midday():
            return self.midnight() - s
        return s


class DB:
    def __init__(self, path):
        self.path = path

    def save(self, value, now=None):
        with dbm.open(self.path, "c") as db:
            db[bytes(Timestamp(now))] = to_bytes(value)

    def save_dict(self, d):
        with dbm.open(self.path, "c") as db:
            for d, v in d.items():
                db[bytes(Timestamp(d))] = to_bytes(v)

    def get(self, now=None):
        now = Timestamp(now)
        with dbm.open(self.path, "c") as db:
            dist = {}
            k = db.firstkey()
            while k is not None:
                t = Timestamp.from_bytes(k)
                dist[t] = abs(now.total_seconds() - t.total_seconds())
                k = db.nextkey(k)
            if len(dist) == 0:
                return None
            dist = sorted(dist.items(), key=lambda i: i[1])
            last = dist[-1]
            if last[0].distance() < dist[0][1]:
                dist[0] = last
            return int(from_bytes(db[bytes(dist[0][0])]))
