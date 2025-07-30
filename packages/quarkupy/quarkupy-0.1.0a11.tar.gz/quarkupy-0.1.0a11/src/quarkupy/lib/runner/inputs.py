from typing import Union

from quarkupy.types.registry.quark.ai import (
    OpenAIEmbeddingRunParams as OpenAIEmbeddingsInput,
    OpenAICompletionBaseRunParams as OpenAICompletionsInput,
)
from quarkupy.types.registry.quark.files import (
    OpendalRunParams as OpendalInput,
    S3ReadFilesBinaryRunParams as S3ReadCSVQuarkInput,
    S3ReadFilesBinaryRunParams as S3ReadWholeFileQuarkInput,
)
from quarkupy.types.registry.quark.vector import (
    LancedbIngestRunParams as VectorDBIngestInput,
    LancedbSearchRunParams as VectorDBSearchInput,
)
from quarkupy.types.registry.quark.databases import SnowflakeReadRunParams as SnowflakeReadInput
from quarkupy.types.registry.quark.extractor import DoclingExtractorRunParams as DocExtractQuarkInput
from quarkupy.types.registry.quark.transformer import (
    DoclingChunkerRunParams as DocChunkerQuarkInput,
    HandlebarsBaseRunParams as TextTemplateInput,
    ParseExtractorLlmRunParams as ParseExtractorLlmInput,
    ParseClassifierLlmRunParams as ParseClassifierLlmInput,
    OnnxSatSegmentationRunParams as SaTSegmentationInput,
    ContextExtractPromptRunParams as ContextExtractPromptInput,
    ContextClassifierPromptRunParams as ContextClassifierPromptInput,
)

QuarkInput = Union[
    ContextClassifierPromptInput,
    ContextExtractPromptInput,
    DocChunkerQuarkInput,
    DocExtractQuarkInput,
    OpenAIEmbeddingsInput,
    OpenAICompletionsInput,
    OpendalInput,
    ParseClassifierLlmInput,
    ParseExtractorLlmInput,
    S3ReadCSVQuarkInput,
    S3ReadWholeFileQuarkInput,
    SaTSegmentationInput,
    SnowflakeReadInput,
    TextTemplateInput,
    VectorDBIngestInput,
    VectorDBSearchInput,
    None,
]

__all__ = [
    "QuarkInput",
    "ContextClassifierPromptInput",
    "ContextExtractPromptInput",
    "DocChunkerQuarkInput",
    "DocExtractQuarkInput",
    "OpenAIEmbeddingsInput",
    "OpenAICompletionsInput",
    "OpendalInput",
    "ParseClassifierLlmInput",
    "ParseExtractorLlmInput",
    "S3ReadCSVQuarkInput",
    "S3ReadWholeFileQuarkInput",
    "SaTSegmentationInput",
    "SnowflakeReadInput",
    "TextTemplateInput",
    "VectorDBIngestInput",
    "VectorDBSearchInput",
]
