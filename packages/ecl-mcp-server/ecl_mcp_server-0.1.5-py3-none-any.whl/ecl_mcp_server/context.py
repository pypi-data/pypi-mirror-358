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

from datetime import timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ecl_mcp_server import constants


class Context(BaseModel):
    """Context information"""

    preferredPoolId: Optional[str] = Field(
        None,
        description="The default resource pool number used when accessing ecl-mcp-server",
    )
    tz: Optional[timezone] = Field(
        None, description="Time zone information, datetime.timezone type"
    )

    http_timeout: float = Field(
        default=constants.HTTP_TIMEOUT, description="HTTP request timeout"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


context = Context(preferredPoolId=None, tz=timezone(timedelta(hours=8)))
