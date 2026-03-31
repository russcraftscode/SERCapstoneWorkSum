import json
import sys
import os
import csv
from pprint import pprint


json_filename = None

if len(sys.argv) > 1: # set the json filename to the user supplied one
    json_filename = sys.argv[1]
else: # get a json file out of the current dir
    print("No filename given, picking 1st json file in directory")
    filenames = os.listdir()
    for filename in filenames:
        if ".json" in filename:
            json_filename = filename

if not json_filename: # if no json file found
    print("Error: Unable to find json project file")
    sys.exit()
print(f"Scraping data from file: {json_filename}")

with open(json_filename , "r") as proj_file:
    proj_json = json.load(proj_file)

task_url_start = "https://tree.taiga.io/project/" + proj_json["slug"] + "/task/"

# get the user story numbers and their total point values
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

print(f"Found {len(user_stories_json)} user stories")

# extract info about tasks
tasks_json = proj_json["tasks"]
tasks = []

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

# identify the team members
team_members = []
for task in tasks: # make a list of all unique team members
    if task["assigned"] not in team_members and task["assigned"]:
        team_members.append(task["assigned"])
print(f"Identified {len(team_members)} team members")
print(team_members)

# Sprint	User Story	Story Points	Link to Task	Coding Task?	tapsey	casteri1	alewi104	rjohn172	bmarti65

# generate lines for the csv output
lines = []
for task in tasks:
    if task["story_number"]:
        line = ["sprint number", "US"+str(task["story_number"]), task["link"], task["points"], " "]
    else:
        line = ["sprint number", "Storyless Task", task["link"], task["points"], " "]
    for team_member in team_members: # put 100% in the proper column
        if team_member == task["assigned"]:
            line.append("100%")
        else:
            line.append("")
    lines.append(line)

with open('draft_work_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['Sprint', 'User Story', 'Points', 'Task Link', 'Coding Task'] + team_members
    #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(lines)