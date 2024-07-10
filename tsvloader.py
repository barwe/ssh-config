import os
import csv
import datetime
from os.path import dirname, exists
from typing import Dict, List, Sequence
from prettytable import PrettyTable
from cipher import AESCipher
from password import PasswordManager

SSH_DIR = os.path.join(os.environ["HOME"], ".ssh")
SSH_CONFIG = os.path.join(SSH_DIR, "config")
DEFAULT_SRC = os.path.join(os.environ.get("HOME"), ".config", "ssh-config", "ssh-config.tsv")

TAB_SIZE = 4
tab = " " * TAB_SIZE
Record = Dict[str, str]
Row = List[str]


class ConfigLoader:

    def __init__(self, src: str = None, password: str = None) -> None:
        self.src = src or DEFAULT_SRC
        if not exists(dirname(src)):
            os.makedirs(dirname(src))
        self.headers = ["Enabled", "Name", "Host", "HostName", "Port", "User", "Password", "Desc"]

        self.password = password
        self.cipher = None
        self.pm = None

    def _validate_password(self):
        pm = PasswordManager(self.src)
        pm.validate(self.password)
        self.cipher = AESCipher.create_with_password(self.password)
        self.pm = pm

    def as_row(self, record: Record) -> Row:
        return [record.get(k, "") for k in self.headers]

    def as_record(self, row: Row) -> Record:
        return {k: v for k, v in zip(self.headers, row)}

    def _encrypt_record(self, record: Record):
        if self.cipher:
            record["Password"] = self.cipher.encrypt(record["Password"])

    def _encrypt_records(self, records: Sequence[Record]):
        if self.cipher:
            for record in records:
                record["Password"] = self.cipher.encrypt(record["Password"])

    def _decrypt_records(self, records: Sequence[Record]):
        if self.cipher:
            for record in records:
                record["Password"] = self.cipher.decrypt(record["Password"])

    def _load_raw(self) -> Sequence[Record]:
        records = []
        if not os.path.exists(self.src):
            return self._dump([])
        reader = open(self.src, "r")
        generator = csv.reader(reader, delimiter="\t")
        try:
            next(generator)
        except StopIteration:
            return self._dump([])
        if len(self.headers) == 0:
            return self._dump([])
        for row in generator:
            records.append(self.as_record(row))
        reader.close()
        return records

    def _load_with_table(self):
        records = self._load_raw()
        table = PrettyTable(self.headers)
        return records, table

    def _dump(self, records: Sequence[Record]) -> Sequence[Record]:
        suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        os.system(f"cp {self.src} {self.src}.{suffix}")
        file = open(self.src, "w")
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(self.headers)
        rows = [self.as_row(record) for record in records]
        writer.writerows(rows)
        file.close()
        return records

    def make(self, write=False):
        self._validate_password()
        blocks = []
        for r in self._load_raw():
            e = "" if r["Enabled"] == "1" else "# "
            items = [f"{e}Host {r['Host']}"]
            items.append(f"{tab}{e}HostName {r['HostName']}")
            if r["Port"] != "22":
                items.append(f"{tab}{e}Port {r['Port']}")
            items.append(f"{tab}{e}User {r['User']}")
            blocks.append("\n".join(items))
        content = "\n\n".join(blocks)
        if write:
            if not os.path.exists(SSH_CONFIG):
                os.system(f"touch {SSH_CONFIG} && chmod 600 {SSH_CONFIG}")
            with open(SSH_CONFIG, "w") as wt:
                wt.write(content)
        else:
            print(content)

    def print(self, keyword: str = None):
        records, table = self._load_with_table()
        if self.password:
            self._validate_password()
            self._decrypt_records(records)
        else:
            for record in records:
                record["Password"] = "[需提供主密码]"

        if keyword is None:
            rows = [self.as_row(r) for r in records]
        else:
            filter = lambda r: keyword in r["Host"] or keyword in r["Name"]
            rows = [self.as_row(r) for r in records if filter(r)]
        table.add_rows(rows)
        print(table)

    def add_item_interactive(self):
        self._validate_password()
        records, table = self._load_with_table()
        record = {}
        record["Host"] = input("Host Key: ").strip()
        record["HostName"] = input("Host Address: ").strip()
        _ = input("Host Port (default: 22): ").strip()
        record["Port"] = "22" if _ == "" else _
        _ = input("Host User (default: root): ").strip()
        record["User"] = "root" if _ == "" else _
        record["Password"] = input("Password (optional): ").strip()
        record["Name"] = input("Name (optional): ").strip()
        record["Desc"] = input("Description (optional): ").strip()
        _ = input("Enabled? (0/1, default: 1): ").strip()
        record["Enabled"] = "1" if _ == "" else _
        self._encrypt_record(record)
        table.add_row(self.as_row(record))
        self._dump([*records, record])
        print(table)

    def remove_item(self, key: str):
        self._validate_password()
        records, table = self._load_with_table()
        removed_hosts = []
        left_records = []
        for record in records:
            if record["Host"] == key:
                table.add_row(self.as_row(record))
                removed_hosts.append(record["Host"])
            else:
                left_records.append(record)

        success = False
        if len(removed_hosts) == 0:
            print("[ERROR] 主机键名无效 %s" % key)
        elif len(removed_hosts) == 1:
            success = True
        else:
            print("[ERROR] 匹配到多个主机 " + ", ".join(removed_hosts))

        if success:
            print(table)
            self._dump(left_records)

        return success

    def update(self, key: str, col: str, val):
        self._validate_password()
        records, table = self._load_with_table()

        success = False
        new_records = []
        for record in records:
            if record["Host"] == key:
                success = True
                record[col] = val
                if "col" == "Password":
                    self._encrypt_record(record)
                table.add_row(self.as_row(record))
            new_records.append(record)

        if success:
            print(table)
            self._dump(new_records)

        return success

    def update_password(self, _new: str, _old: str):
        self.pm = PasswordManager(self.src)
        self.pm.set_password(_new, _old)
        records = self._load_raw()
        self._decrypt_records(records)
        self.cipher = AESCipher.create_with_password(_new)
        self._encrypt_records(records)
        self._dump(records)

    def clean_all_backups(self):
        os.system(f"rm -rf {self.src}.*")

    def open_in_editor(self, target: str):
        if target == "config":
            file = SSH_CONFIG
        else:
            file = self.src
        if os.system(f"code {file}") == 0:
            return
        if os.system(f"nano {file}") == 0:
            return
        if os.system(f"vim {file}") == 0:
            return
        if os.system(f"vi {file}") == 0:
            return
