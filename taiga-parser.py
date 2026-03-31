"""
Filename: taiga-parser.py
Author: Russell Johnson
Date: 2026-3-31
Version: 1.0
Description: This simple script extracts data from a Taiga.com project export
             json file and creates a CSV that is formatted to be copied and
             pasted into a university Semester Work Summary report spreadsheet.
"""
import json
import sys
import os
import csv

# Identify the file that contains the project tata
json_filename = None

if len(sys.argv) > 1:  # set the json filename to the user supplied one
    json_filename = sys.argv[1]
else:  # get a json file out of the current dir
    print("No filename given, picking 1st json file in directory")
    filenames = os.listdir()
    for filename in filenames:
        if ".json" in filename:
            json_filename = filename

if not json_filename:  # if no json file found
    print("Error: Unable to find json project file")
    sys.exit()
print(f"Scraping data from file: {json_filename}")

with open(json_filename , "r") as proj_file:
    proj_json = json.load(proj_file)

task_url_start = "https://tree.taiga.io/project/" + proj_json["slug"] + "/task/"

# Get the user story numbers and their total point values
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

# Extract info about tasks
tasks_json = proj_json["tasks"]
tasks = []

for line in tasks_json:
    task = {
        "story_number": line["user_story"],
        "task_number" : line["ref"],
        "link"        : task_url_start +  str(line["ref"]),
        "assigned"    : line["assigned_to"],
        "sprint"      : line["milestone"]
    }
    # Because sometimes there are storyless tasks that are pointless
    if line["user_story"] in user_stories:
        task["points"] = user_stories[line["user_story"]]
    else:
        task["points"] = "n/a"
    tasks.append(task)

print(f"Extracted {len(tasks)} tasks")

# Identify the team members
team_members = []
for task in tasks:  # make a list of all unique team members
    if task["assigned"] not in team_members and task["assigned"]:
        team_members.append(task["assigned"])
print(f"Identified {len(team_members)} team members")
print(team_members)

# generate lines for the csv output
lines = []
for task in tasks:
    if task["story_number"]:
        line = [ task["sprint"], "US"+str(task["story_number"]), task["points"], task["link"], " "]
    else:
        line = [ task["sprint"], "Storyless Task", task["points"], task["link"], " "]
    for team_member in team_members: # put 100% in the proper column
        if team_member == task["assigned"]:
            line.append("100%")
        else:
            line.append("")
    lines.append(line)

# Etrip email domains out of team member names to leave their ID names
stripped_members = []
for member in team_members:
    stripped_members.append(member.replace("@asu.edu", ""))

with open('draft_work_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['Sprint (needs to be renamed)', 'User Story', 'Points', 'Task Link', 'Coding Task'] + stripped_members
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(lines)

print("Output to 'draft_work_report.csv' .")
