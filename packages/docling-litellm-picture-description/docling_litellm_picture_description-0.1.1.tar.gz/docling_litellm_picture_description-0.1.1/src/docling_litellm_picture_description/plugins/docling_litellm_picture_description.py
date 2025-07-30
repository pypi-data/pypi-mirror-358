from docling_litellm_picture_description.picture_description_litellm_model import \
    PictureDescriptionLiteLLMModel


def picture_description():
    return {
        "picture_description": [
            PictureDescriptionLiteLLMModel,
        ]
    }
