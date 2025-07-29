from typing import Union

from quark.types.registry.quark.ai import (
    OpenAIEmbeddingRunParams as OpenAIEmbeddingsInput,
    OpenAICompletionBaseRunParams as OpenAICompletionsInput,
)
from quark.types.registry.quark.databases import SnowflakeReadRunParams as SnowflakeReadInput
from quark.types.registry.quark.extractor import DoclingExtractorRunParams as DocExtractQuarkInput
from quark.types.registry.quark.files import (
    OpendalRunParams as OpendalInput,
    S3ReadFilesBinaryRunParams as S3ReadCSVQuarkInput,
    S3ReadFilesBinaryRunParams as S3ReadWholeFileQuarkInput,
)
from quark.types.registry.quark.transformer import (
    ContextClassifierPromptRunParams as ContextClassifierPromptInput,
    ContextExtractPromptRunParams as ContextExtractPromptInput,
    DoclingChunkerRunParams as DocChunkerQuarkInput,
    HandlebarsBaseRunParams as TextTemplateInput,
    OnnxSatSegmentationRunParams as SaTSegmentationInput,
    ParseClassifierLlmRunParams as ParseClassifierLlmInput,
    ParseExtractorLlmRunParams as ParseExtractorLlmInput
)
from quark.types.registry.quark.vector import (
    LancedbIngestRunParams as VectorDBIngestInput,
    LancedbSearchRunParams as VectorDBSearchInput,
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
