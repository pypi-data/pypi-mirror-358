from kallia.image_caption_serializer import ImageCaptionSerializer
from kallia.unordered_list_serializer import UnorderedListSerializer
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.datamodel.base_models import InputFormat


class Documents:
    @staticmethod
    def to_markdown(
        source: str, page_number: int, temperature: float, max_tokens: int
    ) -> str:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = True
        ocr_options = RapidOcrOptions()
        pipeline_options.ocr_options = ocr_options

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        page_range = (page_number, page_number)
        converted_doc = converter.convert(source, page_range=page_range).document
        markdown_serializer = MarkdownDocSerializer(
            doc=converted_doc,
            picture_serializer=ImageCaptionSerializer(temperature, max_tokens),
            table_serializer=UnorderedListSerializer(temperature, max_tokens),
        )
        return markdown_serializer.serialize().text
