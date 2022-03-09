"""This module just has environment variables, regexes and exceptions."""

import re

from environs import Env
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

env = Env()
env.read_env()

USER_ID = env.str("USER_ID")
PASSWORD = env.str("PASSWORD")

KILL_BRACKETS_RE = re.compile(r"\s?\(\s?\d+\s?\)")
GROUP_RE = re.compile(
    r"\d(CIFS|BABM|BIS|CL|ECwF|Fin|BMFin|BMMar)\d+|MScBIA|(MAIBM 1)",
    re.IGNORECASE,
)
COURSE_RE = re.compile(r"[3-6]\D+|MSCBIA")

IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException)
