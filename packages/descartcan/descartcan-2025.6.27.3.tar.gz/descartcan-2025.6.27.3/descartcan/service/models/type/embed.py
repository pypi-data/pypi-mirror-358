# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 14:08
# Author     ：Maxwell
# Description：
"""

from enum import Enum


class EmbedModelProperty(object):
    def __init__(self, model_name, dem: int, max_length: int):
        self.model_name = model_name
        self.dem = dem
        self.max_length = max_length


class EmbedModel(Enum):
    M3E = EmbedModelProperty("m3e", dem=768, max_length=512)
    BGE_M3 = EmbedModelProperty("bge_m3", dem=1024, max_length=8192)

    @classmethod
    def get_by_name(cls, name):
        if cls.M3E.value.model_name == name:
            return cls.M3E
        return cls.BGE_M3