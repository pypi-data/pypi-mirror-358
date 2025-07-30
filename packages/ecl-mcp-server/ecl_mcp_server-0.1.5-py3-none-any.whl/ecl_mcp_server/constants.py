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

import os
from datetime import date

ENV_JOURNAL_AK_KEY = "ECLOUD_JOURNAL_ACCESS_KEY"
ENV_JOURNAL_SK_KEY = "ECLOUD_JOURNAL_SECRET_KEY"
ENV_JOURNAL_PREFERRED_POOL_ID = "ECLOUD_JOURNAL_PREFERRED_POOL_ID"
HOST = "https://ecloud.10086.cn"
MODULES = ["default", "group", "theme", "alarm", "dashboard", "etl", "all"]
PACKAGE_NAME = "ecl_mcp_server"
POOL_MAP = [
    {
        "poolId": "CIDC-RP-25",
        "name": "华东 - 苏州",
    },
    {
        "poolId": "CIDC-RP-48",
        "name": "华北 - 呼和浩特",
    },
    {
        "poolId": "CIDC-RP-45",
        "name": "福建 - 厦门",
    },
    {
        "poolId": "CIDC-RP-26",
        "name": "华南 - 广州 3",
    },
]
HTTP_TIMEOUT = 30.0
"""
The timeout for HTTP requests.
"""


def default_server_log_filepath():
    """Generate the default server log file path."""

    ds = date.today().strftime("%Y%m%d")
    return os.path.join(
        os.path.expanduser("~"), ".mcp", "logs", f"ecl_mcp_server_{ds}.log"
    )
