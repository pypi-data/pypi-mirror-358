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

import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

from ecl_mcp_server import constants
from ecl_mcp_server.i18n import _

__all__ = ["NamedPool", "load_pool_map_file"]


class NamedPool(BaseModel):
    """资源池信息"""

    poolId: str = Field(..., description="资源池 ID")
    name: str = Field(..., description="资源池名称")


def load_pool_map_file(filepath: Path):
    """加载资源池映射文件"""

    if not filepath:
        return
    if not filepath.exists():
        logging.warning(_("File: %s does not exist."), filepath)
        return

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            constants.POOL_MAP = [NamedPool.model_validate(m) for m in data]
            logging.debug(
                _("Loaded %s pools: %s"), len(constants.POOL_MAP), constants.POOL_MAP
            )
        except Exception as e:
            logging.warning(
                _("Failed to load Pool resources from file %s."),
                filepath,
                exc_info=e,
            )
