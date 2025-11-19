import re
from typing import Self

__all__ = ["DevSidecarConfig"]


class DevSidecarConfig(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果参数是一个容器，检查其中元素，如果是dict，则该元素也被替换为DevSidecarConfig
        for key, value in list(self.items()):
            if isinstance(value, dict) and not isinstance(value, DevSidecarConfig):
                self[key] = DevSidecarConfig(value)

    def __add__(self, dest: dict | Self, rewrite=True):
        """使用迭代方式合并字典，避免递归深度限制。

        Args:
            dest (dict | Self): 目标字典
            rewrite (bool, optional): 是否允许覆盖目标字典中的同名键。 Defaults to True.

        Returns:
            DevSidecarConfig: 合并后的字典
        """
        if self is None:
            return DevSidecarConfig(dest)

        if dest is None:
            dest = {}

        stack = [(dest, self)]
        while stack:
            target_dict, source_dict = stack.pop()
            for key, value in source_dict.items():
                if key in target_dict:
                    if isinstance(value, dict) and isinstance(target_dict[key], dict):
                        stack.append((target_dict[key], value))
                    elif rewrite:
                        target_dict[key] = value
                else:
                    target_dict[key] = value
        return DevSidecarConfig(dest)

    def __sub__(self, excluded_domains: list[str]) -> Self:
        for k in list(self.keys()):
            if k in excluded_domains:
                self.pop(k)
            elif isinstance(self[k], DevSidecarConfig):
                self[k] -= excluded_domains
        return self

    def __iadd__(self, b):
        return self.__add__(b)

    def __isub__(self, b):
        return self.__sub__(b)
