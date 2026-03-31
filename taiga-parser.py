import json
import sys
from pprint import pprint

with open("project.json" , "r")as proj_file:
    proj_json = json.load(proj_file)

task_url_start = "https://tree.taiga.io/project/" + proj_json["slug"] + "/task/"

# get the user story numbes and thier total point values

user_stories_json = proj_json["user_stories"]
user_stories = {}

for line in user_stories_json:
    story_number = line["ref"]
    points = 0
    if line["role_points"][0]["points"].isnumeric():
        points += int (line["role_points"][0]["points"])
    if line["role_points"][1]["points"].isnumeric():
        points += int (line["role_points"][1]["points"])
    if line["role_points"][2]["points"].isnumeric():
        points += int (line["role_points"][2]["points"])
    if line["role_points"][3]["points"].isnumeric():
        points += int (line["role_points"][3]["points"])
    if line["role_points"][4]["points"].isnumeric():
        points += int (line["role_points"][4]["points"])
    user_stories[story_number] = points

print(f"Found {len(user_stories_json)} tasks")



# extract info about tasks
tasks_json = proj_json["tasks"]
tasks = []

pprint(user_stories_json[0])
#pprint(tasks_json[0])

for line in tasks_json:
    task = {
        "story_number": line["user_story"],
        "task_number" : line["ref"],
        "link"        : task_url_start +  str(line["ref"]),
        "assigned": line["assigned_to"],
    }
    # because sometimes there are storyless tasks that are pointless
    if line["user_story"] in user_stories:
        task["points"] = user_stories[line["user_story"]]
    else:
        task["points"] = "n/a"
    tasks.append(task)

print(f"Extracted {len(tasks)} tasks")
