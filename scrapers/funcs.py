"""Just a collection of random functions used in the scraper scripts."""

import re

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from constants import IGNORED_EXCEPTIONS, KILL_BRACKETS_RE


def sign_in(sel_browser: Chrome, user_id: str, password: str) -> None:
    """Sign in to the intranet site using user_id and password."""
    userid_field = sel_browser.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/section/form/fieldset/div[1]/div/input",
    )
    userid_field.click()
    userid_field.send_keys(user_id)

    password_field = sel_browser.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/section/form/fieldset/div[2]/div/input",
    )
    password_field.click()
    password_field.send_keys(password)
    password_field.send_keys(Keys.ENTER)


def process_location(class_location: str, useless_part: re.Pattern) -> str:
    """Remove unnecessary part from the location string.

    This function's main purpose is to remove the stuff inside (and including)
    brackets from locations like: ATB212 (27) CL, IB303(26), ATB310(25 )B, etc

    Parameters
    ----------
    class_location : str
        where the class is going to be held

    Returns
    -------
    str
        the location without the unnecessary part

    >>> process_location("ATB212 (27) CL", KILL_BRACKETS_RE)
    "ATB212 CL"
    """

    match = re.search(useless_part, class_location)

    if match:
        start, end = match.span()
        class_location = class_location[:start] + class_location[end:]

    return class_location


def process_class_data(class_data: list, slot_index: int) -> dict:
    """Process class data (idk what else to write here).

    Parameters
    ----------
    class_data : list
        looks like: ['location', 'module name_sem_blah_blah', 'teacher name']
    slot_index : int
        the index position of the slot in the timetable (used to figure out
        class time)

    Returns
    -------
    dict
        a dictionary that contains all the processed data (ready to work with)
    """

    if len(class_data) == 2:
        # rn this happens with some 6CL students and theres no location
        class_data.insert(0, "void")

    location, tutor = class_data[0], class_data[2]
    class_name, class_type = class_data[1].split("_", maxsplit=1)
    class_time = 9.0 + (slot_index % 11)

    # i hate to make this code even more loaded, but one module name is
    # incomplete on intranet timetable page (4BABM)
    if class_name.endswith("Beha"):
        class_name += "viour"

    if "lec" in class_type:
        class_type = "lecture"
    elif "w" in class_type:
        class_type = "workshop"
    else:
        class_type = "seminar"

    location = process_location(location, KILL_BRACKETS_RE)

    processed_data = {
        "name": class_name,
        "tutor": tutor,
        "type": class_type,
        "start": class_time,
        "length": 1.0,
        "location": location,
    }

    return processed_data


def select_dropdown_menu(html_id: str, browser: Chrome) -> Select:
    """Wait for dropdown menu to be avaialable in the DOM and select it.

    Parameters
    ----------
    html_id : str
        id of the dropdown menu that needs to be selected
    browser : Chrome
        selenium Chrome webdriver that is used to select the menu

    Returns
    -------
    Select
        the selected dropdown menu
    """

    dropdown = Select(
        WebDriverWait(
            browser, 15, ignored_exceptions=IGNORED_EXCEPTIONS
        ).until(
            expected_conditions.presence_of_element_located((By.ID, html_id))
        )
    )
    return dropdown
