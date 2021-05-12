import csv
import sys
import os.path

os.chdir(os.path.dirname(__file__))

sys.path.append("../safe_string")
from safe_string import safe_string
from safe_sql import has_sqli, is_valid


# https://raw.githubusercontent.com/fthuin/fakepeople/master/fake_people.csv
with open("fake_people.csv", newline="") as fp:
    reader = csv.DictReader(fp)

    print("FALSE POSITIVES")
    print("===============")

    fp = 0
    tot = 0
    rows = 0
    try:
        for template in ["SELECT * FROM people WHERE field = '{}'",
                         'SELECT * FROM people WHERE field = "{}"']:
            template = safe_string._new_trusted(template)
            for row in reader:
                rows += 1
                for value in row.values():
                    query = template.format(value)
                    if is_valid(query):
                        tot += 1
                        if has_sqli(query):
                            print(query)
                            fp += 1

                if rows >= 100:
                    raise StopIteration
    except StopIteration:
        pass
    finally:
        print(f"False positives: {fp}/{tot}")
