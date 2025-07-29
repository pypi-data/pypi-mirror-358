from typing import ClassVar

import quark

from . import QuarkHistoryItem, QuarkRemoteDriver, inputs

TIMEOUT = 3600  # 1 hour


class ClassifierPromptQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:classifier_prompt"

    quark_input: inputs.ContextClassifierPromptInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.context_classifier_prompt.run(**self.quark_input,
                                                                                        timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ClassifierParserQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:Classifier_parser"

    quark_input: inputs.ParseClassifierLlmInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.parse_classifier_llm.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class DocExtractQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:extractor:docling_extractor"

    quark_input: inputs.DocExtractQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.extractor.docling_extractor.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class DocChunkerQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:docling_chunker"

    quark_input: inputs.DocChunkerQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.docling_chunker.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ExtractorPromptQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:extractor_prompt"

    quark_input: inputs.ContextExtractPromptInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.context_extract_prompt.run(**self.quark_input,
                                                                                     timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ExtractorParserQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:extractor_parser"

    quark_input: inputs.ParseExtractorLlmInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.parse_extractor_llm.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpenAICompletionBaseQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:ai:openai_completion_base"

    quark_input: inputs.OpenAICompletionsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.ai.openai_completion_base.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpenAIEmbeddingsQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:ai:openai_embeddings"

    quark_input: inputs.OpenAIEmbeddingsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.ai.openai_embeddings.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpendalReadQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:files:opendal_list_binary"

    quark_input: inputs.OpendalInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.files.opendal.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class S3ReadCSVQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:files:s3_read_csv"

    quark_input: inputs.S3ReadCSVQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.files.s3_read_csv.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class S3ReadWholeFileQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:files:s3_read_files_binary"

    quark_input: inputs.S3ReadWholeFileQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.files.s3_read_files_binary.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class SaTSegmentQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:onnx_sat_segmentation"

    quark_input: inputs.SaTSegmentationInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.onnx_sat_segmentation.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class TextTemplateBaseQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:transformer:handlebars_base"

    quark_input: inputs.TextTemplateInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.transformer.handlebars_base.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class VectorDBIngestQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:vector:lancedb_ingest"

    quark_input: inputs.VectorDBIngestInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.vector.lancedb_ingest.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class VectorDBSearchQuark(QuarkRemoteDriver):
    IDENTIFIER: ClassVar[str] = "quark:vector:lancedb_search"

    quark_input: inputs.VectorDBSearchInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quark.AsyncQuark(base_url=self.BASE_URL)
        res = await api_client.registry.quark.vector.lancedb_search.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


quark_runner_mapping = [
    {
        "identifier": "quark:ai:openai_completion_base",
        "input": inputs.OpenAICompletionsInput,
        "constructor": OpenAICompletionBaseQuark,
    },
    {
        "identifier": "quark:ai:openai_embeddings",
        "input": inputs.OpenAIEmbeddingsInput,
        "constructor": OpenAIEmbeddingsQuark,
    },
    {
        "identifier": "quark:extractor:docling_extractor",
        "input": inputs.DocExtractQuarkInput,
        "constructor": DocExtractQuark,
    },
    {
        "identifier": "quark:files:s3_read_csv",
        "input": inputs.S3ReadCSVQuarkInput,
        "constructor": S3ReadCSVQuark
    },
    {
        "identifier": "quark:files:s3_read_files_binary",
        "input": inputs.S3ReadWholeFileQuarkInput,
        "constructor": S3ReadWholeFileQuark,
    },
    {"identifier": "quark:files:opendal_list_binary",
     "input": inputs.OpendalInput,
     "constructor": OpendalReadQuark,
     },
    {
        "identifier": "quark:transformer:classifier_prompt",
        "input": inputs.ContextClassifierPromptInput,
        "constructor": ClassifierPromptQuark,
    },
    {
        "identifier": "quark:transformer:extractor_prompt",
        "input": inputs.ContextExtractPromptInput,
        "constructor": ExtractorPromptQuark,
    },
    {
        "identifier": "quark:transformer:extractor_parser",
        "input": inputs.ParseExtractorLlmInput,
        "constructor": ExtractorParserQuark,
    },
    {
        "identifier": "quark:transformer:classifier_parser",
        "input": inputs.ParseClassifierLlmInput,
        "constructor": ClassifierParserQuark,
    },
    {
        "identifier": "quark:transformer:onnx_sat_segmentation",
        "input": inputs.SaTSegmentationInput,
        "constructor": SaTSegmentQuark,
    },
    {
        "identifier": "quark:transformer:docling_chunker",
        "input": inputs.DocChunkerQuarkInput,
        "constructor": DocChunkerQuark,
    },
    {
        "identifier": "quark:transformer:handlebars_base",
        "input": inputs.TextTemplateInput,
        "constructor": TextTemplateBaseQuark,
    },
    {
        "identifier": "quark:vector:lancedb_ingest",
        "input": inputs.VectorDBIngestInput,
        "constructor": VectorDBIngestQuark,
    },
    {
        "identifier": "quark:vector:lancedb_search",
        "input": inputs.VectorDBSearchInput,
        "constructor": VectorDBSearchQuark,
    },
]
