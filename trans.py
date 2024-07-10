import csv
from cipher import AESCipher

cipher = AESCipher.create_with_password("--")

target = "/ssh-config.tsv"
rows = []
reader = open(target, "r")
generator = csv.reader(reader, delimiter="\t")
headers = next(generator)
index = headers.index("Password")
for row in generator:
    row[index] = cipher.encrypt(row[index])
    rows.append(row)
reader.close()

file = open(target, "w")
writer = csv.writer(file, delimiter="\t")
writer.writerow(headers)
writer.writerows(rows)
file.close()
