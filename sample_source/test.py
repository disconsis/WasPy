import csv
import safe_sql

# git clone https://github.com/omurugur/SQL_Injection_Payload.git at the same level as WasPy
f = open('../../SQL_Injection_Payload/SQL-Inj-Payload.txt', 'r')
fd = open('result.csv', 'a')
fnames = ['query', 'has_sqli']
writer = csv.DictWriter(fd, fieldnames=fnames)
writer.writeheader()
fn = 0
tot = 0
for x in f:
    for template in ['SELECT * FROM users WHERE name = ', 'SELECT * FROM users WHERE id = ']:
        tot += 1
        value = x
        template += "'" + value + "'"
        if not safe_sql.has_sqli(template) and safe_sql.is_valid(template):
            fn += 1

print("False Negatives:", fn)
print("DONE")
