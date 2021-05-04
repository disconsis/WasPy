
import csv
# git clone https://github.com/omurugur/SQL_Injection_Payload.git at the same level as WasPy
f = open('../../SQL_Injection_Payload/SQL-Inj-Payload.txt','r')
fd = open('result.csv','a') 
fnames = ['query', 'has_sqli']
writer = csv.DictWriter(fd, fieldnames=fnames)
writer.writeheader()
for x in f:
    for template in ['SELECT * FROM users WHERE name = ', 'SELECT * FROM users WHERE id = ']:
        value = x
        template += "'" + value + "'"

        result = "True" if has_sqli(template) else "False"
        writer.writerow({'query' : str(template), 'has_sqli': result})
        
print("DONE")


