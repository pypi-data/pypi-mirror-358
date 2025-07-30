"""
Tests for common models (Answer and SourceDocument).
"""
import pytest
import json
from unittest.mock import Mock, patch
from cwyodmodules.batch.utilities.common.answer import Answer, AnswerEncoder, AnswerDecoder
from cwyodmodules.batch.utilities.common.source_document import SourceDocument


class TestAnswer:
    """Test Answer model functionality."""

    def test_init_with_defaults(self):
        """Test Answer initialization with default parameters."""
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence."
        )
        
        assert answer.question == "What is AI?"
        assert answer.answer == "AI is artificial intelligence."
        assert answer.source_documents == []
        assert answer.prompt_tokens == 0
        assert answer.completion_tokens == 0

    def test_init_with_all_parameters(self):
        """Test Answer initialization with all parameters."""
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Doc",
            source="https://example.com/doc1"
        )
        
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        assert answer.question == "What is AI?"
        assert answer.answer == "AI is artificial intelligence."
        assert len(answer.source_documents) == 1
        assert answer.source_documents[0] == source_doc
        assert answer.prompt_tokens == 10
        assert answer.completion_tokens == 20

    def test_equality_same_answers(self):
        """Test equality comparison for identical answers."""
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Doc",
            source="https://example.com/doc1"
        )
        
        answer1 = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        answer2 = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        assert answer1 == answer2

    def test_equality_different_answers(self):
        """Test equality comparison for different answers."""
        answer1 = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence."
        )
        
        answer2 = Answer(
            question="What is ML?",
            answer="ML is machine learning."
        )
        
        assert answer1 != answer2

    def test_equality_with_non_answer_object(self):
        """Test equality comparison with non-Answer object."""
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence."
        )
        
        assert answer != "not an answer object"
        assert answer != {"question": "What is AI?"}
        assert answer != None

    def test_str_representation_without_sources(self):
        """Test string representation without source documents."""
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence."
        )
        
        result = str(answer)
        assert result == "AI is artificial intelligence."

    def test_str_representation_with_sources(self):
        """Test string representation with source documents."""
        source_doc1 = SourceDocument(
            id="doc1",
            content="Test content 1",
            title="Test Doc 1",
            source="https://example.com/doc1"
        )
        
        source_doc2 = SourceDocument(
            id="doc2",
            content="Test content 2",
            title="Test Doc 2",
            source="https://example.com/doc2"
        )
        
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc1, source_doc2]
        )
        
        result = str(answer)
        expected = ("AI is artificial intelligence.\n\n"
                   "Sources:\n"
                   "[1] Test Doc 1 - https://example.com/doc1\n"
                   "[2] Test Doc 2 - https://example.com/doc2")
        
        assert result == expected

    def test_str_representation_with_sources_no_title(self):
        """Test string representation with source documents without titles."""
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            source="https://example.com/doc1"
        )
        
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc]
        )
        
        result = str(answer)
        expected = ("AI is artificial intelligence.\n\n"
                   "Sources:\n"
                   "[1] Document 1 - https://example.com/doc1")
        
        assert result == expected

    @patch('cwyodmodules.batch.utilities.common.answer.logger')
    def test_to_json(self, mock_logger):
        """Test JSON serialization."""
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Doc",
            source="https://example.com/doc1"
        )
        
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        json_str = answer.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["question"] == "What is AI?"
        assert parsed["answer"] == "AI is artificial intelligence."
        assert parsed["prompt_tokens"] == 10
        assert parsed["completion_tokens"] == 20
        assert len(parsed["source_documents"]) == 1

    @patch('cwyodmodules.batch.utilities.common.answer.logger')
    def test_from_json(self, mock_logger):
        """Test JSON deserialization."""
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        json_data = {
            "question": "What is AI?",
            "answer": "AI is artificial intelligence.",
            "source_documents": [
                '{"id": "doc1", "content": "Test content", "title": "Test Doc", "source": "https://example.com/doc1", "metadata": {}}'
            ],
            "prompt_tokens": 10,
            "completion_tokens": 20
        }
        
        json_str = json.dumps(json_data)
        answer = Answer.from_json(json_str)
        
        assert answer.question == "What is AI?"
        assert answer.answer == "AI is artificial intelligence."
        assert answer.prompt_tokens == 10
        assert answer.completion_tokens == 20
        assert len(answer.source_documents) == 1


class TestAnswerEncoder:
    """Test AnswerEncoder functionality."""

    def test_encode_answer_object(self):
        """Test encoding Answer object."""
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Doc",
            source="https://example.com/doc1"
        )
        
        answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        encoder = AnswerEncoder()
        result = encoder.default(answer)
        
        assert result["question"] == "What is AI?"
        assert result["answer"] == "AI is artificial intelligence."
        assert result["prompt_tokens"] == 10
        assert result["completion_tokens"] == 20
        assert len(result["source_documents"]) == 1

    def test_encode_non_answer_object(self):
        """Test encoding non-Answer object falls back to default behavior."""
        encoder = AnswerEncoder()
        
        with pytest.raises(TypeError):
            encoder.default("not an answer")


class TestAnswerDecoder:
    """Test AnswerDecoder functionality."""

    @patch('cwyodmodules.batch.utilities.common.answer.logger')
    def test_decode_valid_answer_json(self, mock_logger):
        """Test decoding valid Answer JSON."""
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        json_data = {
            "question": "What is AI?",
            "answer": "AI is artificial intelligence.",
            "source_documents": [
                '{"id": "doc1", "content": "Test content", "title": "Test Doc", "source": "https://example.com/doc1", "metadata": {}}'
            ],
            "prompt_tokens": 10,
            "completion_tokens": 20
        }
        
        json_str = json.dumps(json_data)
        decoder = AnswerDecoder()
        answer = decoder.decode(json_str)
        
        assert isinstance(answer, Answer)
        assert answer.question == "What is AI?"
        assert answer.answer == "AI is artificial intelligence."
        assert answer.prompt_tokens == 10
        assert answer.completion_tokens == 20
        assert len(answer.source_documents) == 1

    @patch('cwyodmodules.batch.utilities.common.answer.logger')
    def test_decode_empty_source_documents(self, mock_logger):
        """Test decoding Answer with empty source documents."""
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        json_data = {
            "question": "What is AI?",
            "answer": "AI is artificial intelligence.",
            "source_documents": [],
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        
        json_str = json.dumps(json_data)
        decoder = AnswerDecoder()
        answer = decoder.decode(json_str)
        
        assert isinstance(answer, Answer)
        assert answer.question == "What is AI?"
        assert answer.answer == "AI is artificial intelligence."
        assert answer.source_documents == []

    def test_decode_invalid_json(self):
        """Test decoding invalid JSON raises appropriate error."""
        decoder = AnswerDecoder()
        
        with pytest.raises(json.JSONDecodeError):
            decoder.decode("invalid json")


class TestAnswerIntegration:
    """Test Answer integration scenarios."""

    @patch('cwyodmodules.batch.utilities.common.answer.logger')
    def test_round_trip_serialization(self, mock_logger):
        """Test complete serialization and deserialization cycle."""
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        source_doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Doc",
            source="https://example.com/doc1",
            metadata={"type": "pdf", "pages": 5}
        )
        
        original_answer = Answer(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            source_documents=[source_doc],
            prompt_tokens=15,
            completion_tokens=25
        )
        
        # Serialize to JSON
        json_str = original_answer.to_json()
        
        # Deserialize from JSON
        restored_answer = Answer.from_json(json_str)
        
        # Verify equality
        assert restored_answer == original_answer
        assert restored_answer.question == original_answer.question
        assert restored_answer.answer == original_answer.answer
        assert restored_answer.prompt_tokens == original_answer.prompt_tokens
        assert restored_answer.completion_tokens == original_answer.completion_tokens
        assert len(restored_answer.source_documents) == len(original_answer.source_documents)

    def test_answer_with_multiple_sources_str(self):
        """Test string representation with multiple diverse source documents."""
        sources = []
        for i in range(5):
            source = SourceDocument(
                id=f"doc{i+1}",
                content=f"Content {i+1}",
                title=f"Document {i+1}",
                source=f"https://example.com/doc{i+1}"
            )
            sources.append(source)
        
        answer = Answer(
            question="Complex question?",
            answer="Complex answer with multiple sources.",
            source_documents=sources
        )
        
        result = str(answer)
        
        # Verify answer text
        assert "Complex answer with multiple sources." in result
        
        # Verify all sources are listed
        assert "Sources:" in result
        for i in range(5):
            assert f"[{i+1}] Document {i+1} - https://example.com/doc{i+1}" in result

    def test_answer_edge_cases(self):
        """Test Answer with edge case values."""
        # Empty strings
        answer1 = Answer(question="", answer="")
        assert answer1.question == ""
        assert answer1.answer == ""
        
        # Very large token counts
        answer2 = Answer(
            question="Test",
            answer="Test",
            prompt_tokens=999999,
            completion_tokens=999999
        )
        assert answer2.prompt_tokens == 999999
        assert answer2.completion_tokens == 999999
        
        # None values for optional parameters
        answer3 = Answer(
            question="Test",
            answer="Test",
            source_documents=None,
            prompt_tokens=None,
            completion_tokens=None
        )
        assert answer3.source_documents is None
        assert answer3.prompt_tokens is None
        assert answer3.completion_tokens is None 