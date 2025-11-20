from typing import Self

__all__ = ["ExtendedDict"]


class ExtendedDict(dict):
    """一种支持嵌套，且定义了如何递归合并与按key删减的dict类型。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果参数是一个容器，检查其中元素，如果是dict，则该元素也被替换为ExtendedDict
        for key, value in list(self.items()):
            if isinstance(value, dict) and not isinstance(value, ExtendedDict):
                self[key] = ExtendedDict(value)

    def __add__(self, dest: dict | Self, rewrite=True):
        """使用迭代方式合并字典，避免递归深度限制。

        Args:
            dest (dict | Self): 目标dict
            rewrite (bool, optional): 是否允许覆盖目标dict中的同名键。 Defaults to True.

        Returns:
            ExtendedDict: 合并后的dict
        """
        if self is None:
            return ExtendedDict(dest)

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
        return ExtendedDict(dest)

    def __sub__(self, deleted_keys: list[str]) -> Self:
        """按key删除dict中元素。

        Args:
            deleted_keys (list[str]): dict中待删除的key列表
        Returns:
            Self: 返回删除后的dict。
        """
        for k in list(self.keys()):
            if k in deleted_keys:
                self.pop(k)
            elif isinstance(self[k], ExtendedDict):
                self[k] -= deleted_keys
        return self

    def __iadd__(self, b: dict | Self):
        return self.__add__(b)

    def __isub__(self, b: list[str]):
        return self.__sub__(b)
