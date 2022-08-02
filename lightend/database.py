import dbm.gnu
import logging


def to_bytes(v):
    return str(v).encode()


def from_bytes(b):
    return int(b.decode())


def get_deviations(db, key):
    devs = {}
    k = db.firstkey()
    while k is not None:
        i = from_bytes(k)
        devs[i] = abs(key - i)
        k = db.nextkey(k)
    if len(devs) == 0:
        return None
    return sorted(devs.items(), key=lambda i: i[1])


class DB:
    def __init__(self, path, save_fidelity):
        self.path = path
        self.save_fidelity = save_fidelity

    def save(self, k, v):
        with dbm.open(self.path, "c") as db:
            devs = get_deviations(db, k)
            if devs:
                for d in devs:
                    if d[1] < self.save_fidelity:
                        del db[to_bytes(d[0])]
                        logging.debug("Brightness deleted: %d", d[0])

            db[to_bytes(k)] = to_bytes(v)
            logging.debug("Brightness saved: (%d, %d)", k, v)

    def save_dict(self, d):
        with dbm.open(self.path, "c") as db:
            for k, v in d.items():
                db[to_bytes(k)] = to_bytes(v)

    def get(self, key, max_dev):
        with dbm.open(self.path, "c") as db:
            devs = get_deviations(db, key)
            if not devs:
                return None
            if devs[0][1] > max_dev:
                return False
            return from_bytes(db[to_bytes(devs[0][0])])
