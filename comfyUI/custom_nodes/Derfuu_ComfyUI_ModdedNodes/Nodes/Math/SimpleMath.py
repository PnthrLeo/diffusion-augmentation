import math

import custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.fields as field
from custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.tree import TREE_MATH


class MultiplyNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Value_A": field.FLOAT,
                "Value_B": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "multiply"
    CATEGORY = TREE_MATH

    def multiply(self, Value_A, Value_B):
        total = float(Value_A * Value_B)
        return (total,)


class DivideNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Numerator": field.FLOAT,
                "Denominator": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "divide"
    CATEGORY = TREE_MATH

    def divide(self, Numerator, Denominator):
        total = float(Numerator / Denominator)
        return (total,)


class SumNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Value_A": field.FLOAT,
                "Value_B": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "sum"
    CATEGORY = TREE_MATH

    def sum(self, Value_A, Value_B):
        total = float(Value_A + Value_B)
        return (total,)


class SubtractNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Value_A": field.FLOAT,
                "Value_B": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "sub"
    CATEGORY = TREE_MATH

    def sub(self, Value_A, Value_B):
        total = float(Value_A - Value_B)
        return (total,)


class PowNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Value": field.FLOAT,
                "Exponent": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "pow"
    CATEGORY = TREE_MATH

    def pow(self, Value, Exponent):
        total = math.pow(Value, Exponent)
        return (total,)


class SquareRootNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Value": field.FLOAT,
            },
        }

    RETURN_TYPES = ("FLOAT", "FLOAT",)
    FUNCTION = "sqrt"
    CATEGORY = TREE_MATH

    def sqrt(self, Value):
        total = math.sqrt(Value)
        return (total, -total,)