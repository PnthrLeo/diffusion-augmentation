import custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.sizes as sizes
from custom_nodes.Derfuu_ComfyUI_ModdedNodes.components.tree import TREE_FUNCTIONS


class GetLatentSize:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",),
                "original": ([False, True],),
            }
        }

    RETURN_TYPES = ("INT", "INT", "TUPLE",)
    CATEGORY = TREE_FUNCTIONS

    FUNCTION = 'get_size'

    def get_size(self, latent, original):
        size = sizes.get_latent_size(latent, original)
        return (size[0], size[1], size,)


class GetImageSize:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("INT", "INT", "TUPLE",)
    CATEGORY = TREE_FUNCTIONS

    FUNCTION = 'get_size'

    def get_size(self, image):
        size = sizes.get_image_size(image)
        return (size[0], size[1], size, )