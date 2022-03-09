"""
Scrapes groups on the intranet timetable page. Gets all the lessons data for
undergrad, saves it in .json format in the data folder.
"""

import json
import logging
from pathlib import Path
import random
import re
import shutil
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from constants import COURSE_RE, GROUP_RE, PASSWORD, USER_ID
from funcs import process_class_data, select_dropdown_menu, sign_in
from loader import browser


# delete old timetable data
shutil.rmtree("./timetable/", ignore_errors=True)

# make a GET request to intranet timetable
browser.get("https://intranet.wiut.uz/TimeTableNew/GetLessons")
sign_in(browser, USER_ID, PASSWORD)

try:
    dropdown = select_dropdown_menu("ddlclass", browser)
except TimeoutException:
    browser.quit()
    raise SystemExit("No groups were found. No timetable available.")

# this is just a list of all undergrad + MSCBIA group names
all_groups = [
    option.text
    for option in dropdown.options
    if re.search(GROUP_RE, option.text)
]

for group in all_groups:
    if group == "MAIBM 1":
        continue

    logging.info(f"Getting data for {group}")

    dropdown = select_dropdown_menu("ddlclass", browser)
    dropdown.select_by_visible_text(group)

    # slots -> all boxes that contain info on classes
    # there are 66 of them, 11 per day for 6 days (Monday-Saturday)
    slots = browser.find_elements(
        By.CSS_SELECTOR,
        "div.innerbox[style='overflow-y: auto; overflow-x: hidden;  "
        "font-size:medium']",
    )

    days = {str(n): [] for n in range(8)}

    for index, slot in enumerate(slots):
        # no class in this time slot
        if not slot.text:
            continue

        day = str((index // 11) + 1)

        # this whole script works thanks to the fact that all class details
        # are formatted more or less the same
        data = slot.text.splitlines()

        # removing the group names from this list so that it looks like:
        # ['some location', 'module name_sem_blah_blah', 'teacher name']
        data = [entry for entry in data if not re.search(GROUP_RE, entry)]

        # splitting the data list into sublists because sometimes theres more
        # than 1 class scheduled in 1 time slot
        # [., ., ., ., ., .] -> [[...], [...]]
        classes_data = [data[i : i + 3] for i in range(0, len(data), 3)]

        for data in classes_data:
            processed_data = process_class_data(data, index)

            # if theres a collision -> 2 or more classes in one time slot:
            # we want to check the length of the last and prelast class
            if len(classes_data) > 1:
                end = -3
            else:
                end = -2

            for i in range(-1, end, -1):
                try:
                    past_class = days[day][i]
                except IndexError:
                    past_class = {}

                # conditions for the if check (it got messy without them)
                same_name = past_class.get("name") == processed_data["name"]
                same_type = past_class.get("type") == processed_data["type"]

                # Subair's lectures - 1hour lecture & 1hour workshop, but many
                # consider this 2-hour lecture, it will be classified like that
                edge_case = (
                    past_class.get("type") == "lecture"
                    and past_class.get("name") == processed_data["name"]
                    and processed_data["type"] == "workshop"
                    and past_class.get("length") == 1
                )

                if past_class and same_name and (same_type or edge_case):
                    past_class["length"] += 1.0
                    # if we break, the else block won't run
                    break
            else:
                days[day].append(processed_data)

    group = group.upper()
    course = re.search(COURSE_RE, group)
    assert course is not None
    course = course.group()

    # creating the relevant dir if it doesn't exit
    Path(f"./timetable/{course}").mkdir(parents=True, exist_ok=True)

    with open(f"./timetable/{course}/{group}.json", "w") as output:
        json.dump(days, output, indent=2)

    # to be on the safe side and not send a ton of requests in a short time
    # random is used so that it seems like a human is actually doing this
    time.sleep(random.uniform(2, 3))

browser.quit()
