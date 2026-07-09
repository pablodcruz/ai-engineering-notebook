from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from enablement_assistant.answer import synthesize_answer
from enablement_assistant.documents import build_chunks, load_markdown_documents
from enablement_assistant.retrieval import TfIdfRetriever


FIXTURE_CORPUS = Path(__file__).parent / "fixtures" / "corpus"


class AssistantTests(unittest.TestCase):
    def test_loads_markdown_with_source_metadata(self) -> None:
        documents = load_markdown_documents(FIXTURE_CORPUS)
        chunks = build_chunks(documents, target_words=60)

        self.assertTrue(chunks)
        self.assertIn(chunks[0].source_path, {"projects.md", "rag.md"})
        self.assertTrue(all(chunk.start_line <= chunk.end_line for chunk in chunks))
        self.assertTrue(all(chunk.heading for chunk in chunks))

    def test_retrieves_expected_source(self) -> None:
        chunks = build_chunks(load_markdown_documents(FIXTURE_CORPUS))
        retriever = TfIdfRetriever.from_chunks(chunks)

        results = retriever.search("What makes answers auditable?", top_k=3)

        self.assertTrue(results)
        self.assertEqual(results[0].chunk.source_path, "rag.md")
        self.assertIn("Traceability", results[0].chunk.heading)

    def test_answer_includes_citation_when_grounded(self) -> None:
        chunks = build_chunks(load_markdown_documents(FIXTURE_CORPUS))
        retriever = TfIdfRetriever.from_chunks(chunks)

        answer = synthesize_answer(
            "What should project documentation include?",
            retriever.search("What should project documentation include?"),
        )

        self.assertTrue(answer.found)
        self.assertIn("[S1]", answer.answer)
        self.assertTrue(answer.citations)
        self.assertEqual(answer.citations[0].source_path, "projects.md")

    def test_not_found_for_uncovered_question(self) -> None:
        chunks = build_chunks(load_markdown_documents(FIXTURE_CORPUS))
        retriever = TfIdfRetriever.from_chunks(chunks)

        answer = synthesize_answer(
            "What is the capital of France?",
            retriever.search("What is the capital of France?"),
        )

        self.assertFalse(answer.found)
        self.assertEqual(answer.citations, [])


if __name__ == "__main__":
    unittest.main()
