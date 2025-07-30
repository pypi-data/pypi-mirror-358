"""
This module has been programmed to need the
'yta_image_advanced' only if you are using the
'Image' class that this file contains.
"""
from yta_image_advanced_ai.descriptor import DefaultImageDescriptor
from yta_programming.decorators.requires_dependency import requires_dependency


class Image:
    """
    TODO: Do I need to put the description here
    instead of in the '_Image' instance I return (?)
    """

    @requires_dependency('yta_image_advanced', 'yta_image_advanced_ai', 'yta_image_advanced')
    def __new__(
        cls,
        *args,
        **kwargs
    ):
        try:
            from yta_image_advanced import Image as AdvancedImage
        except ImportError as e:
            raise ImportError(
                f'The "Image" class of this module needs the "yta_image_advanced" module installed.'
            ) from e

        class _Image(AdvancedImage):
            """
            Advanced Image class that includes AI-related
            functionality.
            """

            @property
            def description(
                self
            ) -> str:
                """
                A description of the image, given by an engine that
                has been trained to describe images.
                """
                if not hasattr(self, '_description'):
                    self._description = DefaultImageDescriptor().describe(self.image)

                return self._description
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        
        instance = _Image(*args, **kwargs)

        return instance