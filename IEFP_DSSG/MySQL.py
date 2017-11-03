import pymysql

conn = pymysql.connect(host='151.236.42.86', port=3306, user='grupo_1', passwd='bi4ever', db='iefp')
cur = conn.cursor()

cur.execute("SELECT * FROM sie_31 LIMIT 10")
#print(cur.description)

for row in cur:
    print(row)

cur.close()
conn.close()
