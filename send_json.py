import json

class Status:

    def __init__(self, obj_name):
        self.filename = "status.json"
        self.obj = obj_name


    def reset(self):
        with open(self.filename, "w") as f:
            f.write("""{
              "server":0,
              "target":{"1":0, "2":0}
            }""")


    def write_status(self, state):
        with open(self.filename, "r") as f:
            data = json.load(f)
        if self.obj == "server":
            data["server"]= state
        elif self.obj == "target1":
            print("\n\ntestetes")
            print(state)
            data["target"]["1"] = state
        elif self.obj == "target2":
            data["target"]["2"]= state
        with open(self.filename, "w") as f:
            json.dump(data, f)
            print(data)



class jsonPipe:

    def __init__(self):
        self.filename = "data.json"
        self.reset()

    def reset(self):
        with open(self.filename, "w") as f:
            f.write('''{"target": {"1": [], "2": []}}''')

    def write_zones(self, target, zones):
        with open(self.filename, "r") as f:
            data = json.load(f)
        targets = data["target"]
        zones_placeholder = targets[str(target)]["zones"]
        for zone in zones:
            zones_placeholder.append(zone)
        with open(self.filename, "w") as f:
            json.dump(data, f)

    def write_impact(self, target, impacts, point):
        serialized = [(float(impacts[i][0]), float(impacts[i][1]), int(point[i])) for i in range(len(impacts))]
        print("\n",impacts)
        with open(self.filename, "r") as f:
            data = json.load(f)
        targets = data["target"]
        targets[str(target)] = [impact for impact in serialized]
        print("data", data)
        with open(self.filename, "w") as f:
            json.dump(data, f)



#
# jsonpipe = jsonPipe()
# jsonpipe.write_zones(1, [(1234,1234), (87654,876)])
# jsonpipe.write_status("target2", "waiting", 1)
