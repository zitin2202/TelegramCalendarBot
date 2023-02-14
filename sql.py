import _sqlite3

base = _sqlite3.connect('database.db')
cur = base.cursor()

base.execute('CREATE TABLE IF NOT EXISTS users(id PRIMARY KEY, token)')
base.commit()
#
# cur.execute('INSERT INTO users VALUES(?,?)',('1234','Я'))
# cur.execute('INSERT INTO users VALUES(?,?)',('2342','ТЫ'))
# base.commit()

# r = cur.execute('SELECT * FROM users').fetchall()
# print(r)
# cur.execute('DELETE FROM users')
# base.commit()



# c = cur.execute('SELECT * FROM users')
#
# for row in cur:
#     print(row)