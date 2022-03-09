"""
Scrape intranet timetable page and find all empty rooms (empty timeslots).
A .json file is generated for each day in the week and looks sth like:

{
  "9.0": [
    "ATB207",
    "ATB307",
    ...
  ],
  "10.0": [
    "ATB207",
    "ATB307",
    ...
  ],
  ...
}

"""

from copy import deepcopy
import json
import logging
from pathlib import Path
import random
import shutil
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from constants import KILL_BRACKETS_RE, PASSWORD, USER_ID
from funcs import process_location, select_dropdown_menu, sign_in
from loader import browser

# delete old rooms data
shutil.rmtree("./rooms/", ignore_errors=True)

browser.get("https://intranet.wiut.uz/TimeTableNew/GetLessons")
sign_in(browser, USER_ID, PASSWORD)

try:
    dropdown = select_dropdown_menu("ddlclassroom", browser)
except TimeoutException:
    browser.quit()
    raise SystemExit("No classrooms were found. No timetable available.")

# all classrooms excluding lyceum rooms
classrooms = [
    option.text for option in dropdown.options if "Lyceum" not in option.text
]

time_slots = {
    "9.0": [],
    "10.0": [],
    "11.0": [],
    "12.0": [],
    "13.0": [],
    "14.0": [],
    "15.0": [],
    "16.0": [],
    "17.0": [],
    "18.0": [],
    "19.0": [],
}

list_of_days = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]

data = {day: deepcopy(time_slots) for day in list_of_days}

# first field in classroom dropdown menu is empty
for room in classrooms[1:]:
    logging.info(f"Checking room: {room}")

    dropdown = select_dropdown_menu("ddlclassroom", browser)
    dropdown.select_by_visible_text(room)

    # slots -> all boxes that contain info on classes
    # there are 66 of them, 11 per day for 6 days (Monday-Saturday)
    slots = browser.find_elements(
        By.CSS_SELECTOR,
        "div.innerbox[style='overflow-y: auto; overflow-x: hidden;  "
        "font-size:medium']",
    )

    for index, slot in enumerate(slots):
        # this slot is busy, some class going on
        if slot.text:
            continue

        day = index // 11
        class_time = 9.0 + (index % 11)

        room = process_location(room, KILL_BRACKETS_RE)
        data[list_of_days[day]][str(class_time)].append(room)

    time.sleep(random.uniform(2, 3))

# creating the relevant dir if it doesn't exit
Path(f"./rooms").mkdir(parents=True, exist_ok=True)

for day in list_of_days:
    with open(f"./rooms/{day}.json", "w") as output:
        json.dump(data[day], output, indent=2)

browser.quit()
