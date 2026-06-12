from .bernini_patches import apply_bernini_patches

apply_bernini_patches()

from .nodes_bernini import comfy_entrypoint  # noqa: F401

WEB_DIRECTORY = "./web"

__all__ = ["WEB_DIRECTORY"]
