#  Copyright © 2025 China Mobile (SuZhou) Software Technology Co.,Ltd
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
import gettext
import importlib.resources
import locale
import os
import sys
from pathlib import Path

import ecl_mcp_server.constants as constants

__all__ = ["_"]


def _get_locale_dir() -> str:
    #  Try package resource path (built environment)
    try:
        pkg_dir = importlib.resources.files(constants.PACKAGE_NAME)
        package_locale = pkg_dir / "locales"
        if package_locale.is_dir():
            return str(package_locale)
    except (ImportError, TypeError):
        pass

    # dev environment：base on project root dir
    #  Method 1: Trace back to project root via __file__
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent  # src/ecl_mcp_server -> src -> root

    #  Method 2: Dynamically find root dir containing pyproject.toml
    if not (project_root / "pyproject.toml").exists():
        project_root = Path.cwd()
        while not (project_root / "pyproject.toml").exists() and project_root.parent != project_root:
            project_root = project_root.parent

    #  Check locales directory
    dev_locale = project_root / "locales"
    if dev_locale.exists():
        return str(dev_locale)

    #  Fallback to package resources
    return str(package_locale)


def _get_translation():
    current_lang, enc = locale.getdefaultlocale()
    if current_lang is None:
        current_lang = os.environ.get("LANG", "en_US")[:5]
    locale_dir = _get_locale_dir()
    print(f"{datetime.datetime.now()} [ecl-mcp-server] locale dir: {locale_dir}", file=sys.stderr)
    _translation = gettext.translation("messages", localedir=str(locale_dir), languages=[current_lang], fallback=True)
    return _translation.gettext


_ = _get_translation()
