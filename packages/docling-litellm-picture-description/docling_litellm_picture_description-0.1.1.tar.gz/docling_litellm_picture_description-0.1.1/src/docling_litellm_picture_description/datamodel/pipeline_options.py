from typing import Any, ClassVar, Dict, Literal

from docling.datamodel.pipeline_options import PictureDescriptionBaseOptions


class PictureDescriptionLiteLLMOptions(PictureDescriptionBaseOptions):
    kind: ClassVar[Literal["litellm"]] = "litellm"

    model: str
    timeout: float = 30.0
    params: Dict[str, Any] = {}
    concurrency: int = 1

    prompt: str = "Describe this image in a few sentences."
