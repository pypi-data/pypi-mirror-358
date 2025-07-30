from typing import ClassVar, Literal

from docling.datamodel.pipeline_options import PictureDescriptionBaseOptions


class PictureDescriptionLiteLLMOptions(PictureDescriptionBaseOptions):
    kind: ClassVar[Literal["litellm"]] = "litellm"

    model: str
    timeout: float = 30.0
    concurrency: int = 1

    prompt: str = "Describe this image in a few sentences."
