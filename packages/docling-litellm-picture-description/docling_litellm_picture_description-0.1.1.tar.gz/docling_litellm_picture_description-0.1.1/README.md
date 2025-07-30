# Docling LiteLLM Picture Description Plugin

This plugin allows you to use the [LiteLLM](https://github.com/BerriAI/litellm) library for generating picture descriptions in your Docling pipeline. This plugin will allow you to use Vision LLM from any external providers supported by LiteLLM, such as OpenAI, Azure OpenAI, Vertex AI, and xAI.

## Installation

```bash
pip install docling-litellm-picture-description
```

## Usage

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_litellm_picture_description.datamodel.pipeline_options import PictureDescriptionLiteLLMOptions

picture_description_options = PictureDescriptionApiOptions(
    model=self.model_name,
    prompt="Describe the picture in detail.",
    scale=1.0,
    timeout=120,
)
pipeline_options = PdfPipelineOptions(
    enable_remote_services=True,
    allow_external_plugins=True,
    do_picture_description=True,
    picture_description_options=picture_description_options,
    generate_picture_images=True,
)
converter = DocumentConverter(
    format_options={
        InputFormat.IMAGE: PdfFormatOption(
            pipeline_options=pipeline_options,
        ),
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)
doc = converter.convert(file).document
markdown_text = doc.export_to_markdown()
```
