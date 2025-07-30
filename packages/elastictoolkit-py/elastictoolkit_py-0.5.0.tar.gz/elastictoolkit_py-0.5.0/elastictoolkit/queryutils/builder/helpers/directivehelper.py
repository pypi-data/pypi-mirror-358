import warnings
from typing import Callable


class DirectiveHelper:
    # NOTE: This class is deprecated. Use `ValueTransformer` instead. | Reason: Suboptimal name
    warnings.warn(
        "DirectiveHelper is deprecated. Use `ValueTransformer` instead.",
        DeprecationWarning,
    )

    """Helper class for directives"""

    @staticmethod
    def unpacked(func: Callable):
        """
        Sets a property `unpack` to True. This signals `ValueParser` to unpack values
        when appending items to list when calling this func.
        """
        func.unpack = True
        return func

    @staticmethod
    def normalize_str(param: str):
        def normalize_func(match_params):
            return str.lower(match_params[param])

        return normalize_func
