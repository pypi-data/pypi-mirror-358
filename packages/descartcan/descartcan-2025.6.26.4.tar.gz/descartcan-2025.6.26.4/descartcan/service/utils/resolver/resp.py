# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/25 21:51
# Author     ：Maxwell
# Description：
"""

import json
import traceback
from typing import Any
from descartcan.utils.log import logger


def get_data_from_text(text) -> (bool, Any):
    try:
        result = json.loads(text)
        result_code = result.get("code")
        if result_code != 200:
            return False, result.get("message")
        return True, result.get("data")
    except Exception as e:
        logger.info(f"get_data_from_text error: {traceback.format_exc()}")
        return False, None
