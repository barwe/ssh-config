import sys
import hashlib
from os.path import dirname, join, exists


def hash_password(password: str):
    if password:
        password = hashlib.sha256(password.encode()).hexdigest()
    return password


class PasswordManager:
    def __init__(self, srctsv: str):
        self.srcfile = join(dirname(srctsv), "password")
        self.cipher = None

    def load_from_file(self):
        if not exists(self.srcfile):
            return None
        with open(self.srcfile) as r:
            return r.read().strip()

    def dump_to_file(self, hashed_password: str):
        with open(self.srcfile, "w") as w:
            w.write(hashed_password)

    def _validate(self, password: str):
        saved_password = self.load_from_file()
        if saved_password is None:
            print("[ERROR] 请先设置主密码 ~ passwd <password>")
            sys.exit(1)
        if saved_password != password:
            print("[ERROR] 主密码验证失败")
            sys.exit(1)
        return True

    def validate(self, password: str):
        password = hash_password(password)
        self._validate(password)

    def set_password(self, new_password: str, old_password: str = None):
        new_password = hash_password(new_password)
        old_password = hash_password(old_password)
        if self._validate(old_password):
            self.dump_to_file(new_password)
