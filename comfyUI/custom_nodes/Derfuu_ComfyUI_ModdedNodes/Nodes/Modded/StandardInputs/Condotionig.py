import math

import custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.fields as field
from custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.tree import TREE_COND
import custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.sizes as sizes


class ConditioningAreaScale_Ratio:
    def __init__(self):
        pass


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning": ('CONDITIONING',),
                "modifier": field.FLOAT,
                "strength_modifier": field.FLOAT,
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "resize"
    CATEGORY = TREE_COND

    def resize(self, conditioning, modifier, strength_modifier, min_sigma=0.0, max_sigma=99.0):
        c = []

        for t in conditioning:
            n = [t[0], t[1].copy()]

            try:
                size, offset = sizes.get_conditioning_size(n[1])
            except:
                c.append(n)
                continue

            height = int(size["height"] * 8 * modifier)
            width = int(size["width"] * 8 * modifier)

            y = int(offset["y_offset"] * 8 * modifier)
            x = int(offset["x_offset"] * 8 * modifier)

            n[1]['area'] = (height // 8, width // 8, y // 8, x // 8)
            n[1]['strength'] *= strength_modifier
            n[1]['min_sigma'] = min_sigma
            n[1]['max_sigma'] = max_sigma
            c.append(n)

        return (c,)