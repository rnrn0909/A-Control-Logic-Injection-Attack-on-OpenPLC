import sqlite3
import datetime
import fnmatch
import os

warning = "Searching the location of database"
print(warning.center(80, "."))

path = '/'
whereareyou = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(path) for f in fnmatch.filter(files, 'openplc.db')]

if len(whereareyou) < 1:
    print("[x] Can't find installation ")
    exit()
else:
    print("[+] OpenPLC is installed: ", os.path.dirname(whereareyou[0]))

conn = sqlite3.connect(whereareyou[0])
cursor = conn.cursor()
print('[+] Connected to DB. ')

print()
title1 = "Users"
print(title1.center(80, "-"))
cmd1 = cursor.execute("SELECT * FROM Users")
result = cmd1.fetchall()
for uid, name, username, email, pwd, pict in result:
    print(f'{uid}: {name} | {username} | {email} | {pwd} | {pict}')

print()
title2 = "Programs"
print(title2.center(80, "-"))
cmd2 = cursor.execute("SELECT * FROM Programs")
fetch_progs = cmd2.fetchall()
for pid, prog_name, desc, prog_file, date_upload in fetch_progs:
    uploaded = datetime.datetime.fromtimestamp(date_upload).strftime('%c')
    print(f'{pid}: {prog_name} | {prog_file} | {uploaded}')
print()


#
# title3 = "How to manipulate"
# print(title3.center(80, '-'))
# theendoftheword = datetime.datetime.strftime(parse('21.12.2012 12:21:12'), '%s')
# cmd3 = cursor.execute(f"UPDATE Programs SET Date_upload = \'{theendoftheword}\' WHERE Prog_ID = 24")
# conn.commit()

# cmd4 = cursor.execute("SELECT * FROM Programs WHERE Prog_ID = 24")
# show = cmd4.fetchone()
# conversion = datetime.datetime.fromtimestamp(show[4]).strftime('%c')
# print(f'{show[0]}: {show[1]} | {show[3]} | {conversion}')