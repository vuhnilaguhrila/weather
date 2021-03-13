import json

us_cities = []
with open("city.list.json", "r") as f:
    content = json.load(f)

    for item in content:
        if item["country"] == "US":
            if item["state"]:
                temp_dict = {}
                temp_dict["state"] = item["state"]
                temp_dict["city"] = item["name"]
                temp_dict["id"] = item["id"]
                temp_dict["coord"]= item["coord"]
                us_cities.append(temp_dict)

print(us_cities)

with open("us_cities.json", "w") as f:
    json.dump(us_cities, f, indent = 4)


with open("us_cities.json", "r") as f:
    content = json.load(f)

    for item in content:
        if not item["state"]:
            print(item)
    timezones = []
    for item in content:
        if item["timezone"] not in timezones:
            timezones.append(item["timezone"])
    print(timezones)

