"""
Tests for SourceDocument model.
"""
import pytest
import json
from unittest.mock import Mock, patch
from cwyodmodules.batch.utilities.common.source_document import SourceDocument


class TestSourceDocumentInitialization:
    """Test SourceDocument initialization."""

    def test_init_with_required_parameters(self):
        """Test SourceDocument initialization with required parameters."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        assert doc.id == "doc1"
        assert doc.content == "Test content"
        assert doc.title == "Test Document"
        assert doc.source == "https://example.com/doc1"
        assert doc.metadata == {}

    def test_init_with_all_parameters(self):
        """Test SourceDocument initialization with all parameters."""
        metadata = {"type": "pdf", "pages": 5, "author": "John Doe"}
        
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata=metadata
        )
        
        assert doc.id == "doc1"
        assert doc.content == "Test content"
        assert doc.title == "Test Document"
        assert doc.source == "https://example.com/doc1"
        assert doc.metadata == metadata

    def test_init_with_none_values(self):
        """Test SourceDocument initialization with None values."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title=None,
            source="https://example.com/doc1",
            metadata=None
        )
        
        assert doc.id == "doc1"
        assert doc.content == "Test content"
        assert doc.title is None
        assert doc.source == "https://example.com/doc1"
        assert doc.metadata is None

    def test_init_with_empty_strings(self):
        """Test SourceDocument initialization with empty strings."""
        doc = SourceDocument(
            id="",
            content="",
            title="",
            source=""
        )
        
        assert doc.id == ""
        assert doc.content == ""
        assert doc.title == ""
        assert doc.source == ""
        assert doc.metadata == {}


class TestSourceDocumentEquality:
    """Test SourceDocument equality comparisons."""

    def test_equality_identical_documents(self):
        """Test equality for identical documents."""
        metadata = {"type": "pdf", "pages": 5}
        
        doc1 = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata=metadata
        )
        
        doc2 = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata=metadata
        )
        
        assert doc1 == doc2

    def test_equality_different_ids(self):
        """Test inequality for documents with different IDs."""
        doc1 = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        doc2 = SourceDocument(
            id="doc2",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        assert doc1 != doc2

    def test_equality_different_content(self):
        """Test inequality for documents with different content."""
        doc1 = SourceDocument(
            id="doc1",
            content="Content 1",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        doc2 = SourceDocument(
            id="doc1",
            content="Content 2",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        assert doc1 != doc2

    def test_equality_different_metadata(self):
        """Test inequality for documents with different metadata."""
        doc1 = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata={"type": "pdf"}
        )
        
        doc2 = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata={"type": "docx"}
        )
        
        assert doc1 != doc2

    def test_equality_with_non_source_document(self):
        """Test inequality with non-SourceDocument objects."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        assert doc != "not a document"
        assert doc != {"id": "doc1", "content": "Test content"}
        assert doc != None
        assert doc != 123


class TestSourceDocumentStringRepresentation:
    """Test SourceDocument string representation."""

    def test_str_with_title(self):
        """Test string representation with title."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        result = str(doc)
        assert "Test Document" in result
        assert "https://example.com/doc1" in result

    def test_str_without_title(self):
        """Test string representation without title."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title=None,
            source="https://example.com/doc1"
        )
        
        result = str(doc)
        assert "doc1" in result
        assert "https://example.com/doc1" in result

    def test_str_with_empty_title(self):
        """Test string representation with empty title."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="",
            source="https://example.com/doc1"
        )
        
        result = str(doc)
        assert "doc1" in result
        assert "https://example.com/doc1" in result


class TestSourceDocumentSerialization:
    """Test SourceDocument serialization and deserialization."""

    def test_to_json_with_all_fields(self):
        """Test JSON serialization with all fields."""
        metadata = {"type": "pdf", "pages": 5, "author": "John Doe"}
        
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1",
            metadata=metadata
        )
        
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["id"] == "doc1"
        assert parsed["content"] == "Test content"
        assert parsed["title"] == "Test Document"
        assert parsed["source"] == "https://example.com/doc1"
        assert parsed["metadata"] == metadata

    def test_to_json_with_minimal_fields(self):
        """Test JSON serialization with minimal fields."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title="Test Document",
            source="https://example.com/doc1"
        )
        
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["id"] == "doc1"
        assert parsed["content"] == "Test content"
        assert parsed["title"] == "Test Document"
        assert parsed["source"] == "https://example.com/doc1"
        assert parsed["metadata"] == {}

    def test_to_json_with_none_values(self):
        """Test JSON serialization with None values."""
        doc = SourceDocument(
            id="doc1",
            content="Test content",
            title=None,
            source="https://example.com/doc1",
            metadata=None
        )
        
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["id"] == "doc1"
        assert parsed["content"] == "Test content"
        assert parsed["title"] is None
        assert parsed["source"] == "https://example.com/doc1"
        assert parsed["metadata"] is None

    def test_from_json_with_all_fields(self):
        """Test JSON deserialization with all fields."""
        json_data = {
            "id": "doc1",
            "content": "Test content",
            "title": "Test Document",
            "source": "https://example.com/doc1",
            "metadata": {"type": "pdf", "pages": 5}
        }
        
        json_str = json.dumps(json_data)
        doc = SourceDocument.from_json(json_str)
        
        assert doc.id == "doc1"
        assert doc.content == "Test content"  
        assert doc.title == "Test Document"
        assert doc.source == "https://example.com/doc1"
        assert doc.metadata == {"type": "pdf", "pages": 5}

    def test_from_json_with_minimal_fields(self):
        """Test JSON deserialization with minimal fields."""
        json_data = {
            "id": "doc1",
            "content": "Test content",
            "title": "Test Document",
            "source": "https://example.com/doc1",
            "metadata": {}
        }
        
        json_str = json.dumps(json_data)
        doc = SourceDocument.from_json(json_str)
        
        assert doc.id == "doc1"
        assert doc.content == "Test content"
        assert doc.title == "Test Document"
        assert doc.source == "https://example.com/doc1"
        assert doc.metadata == {}

    def test_from_json_invalid_json(self):
        """Test JSON deserialization with invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            SourceDocument.from_json("invalid json")

    def test_from_json_missing_required_fields(self):
        """Test JSON deserialization with missing required fields."""
        json_data = {
            "id": "doc1",
            "content": "Test content"
            # Missing title and source
        }
        
        json_str = json.dumps(json_data)
        
        with pytest.raises(KeyError):
            SourceDocument.from_json(json_str)


class TestSourceDocumentRoundTripSerialization:
    """Test round-trip serialization scenarios."""

    def test_round_trip_with_complete_document(self):
        """Test complete serialization and deserialization cycle."""
        metadata = {
            "type": "pdf",
            "pages": 10,
            "author": "Jane Smith",
            "created_date": "2024-01-01",
            "tags": ["research", "AI", "machine learning"]
        }
        
        original_doc = SourceDocument(
            id="complex_doc_123",
            content="This is a complex document with various metadata fields and content.",
            title="Complex Research Document",
            source="https://research.example.com/papers/complex_doc_123.pdf",
            metadata=metadata
        )
        
        # Serialize to JSON
        json_str = original_doc.to_json()
        
        # Deserialize from JSON
        restored_doc = SourceDocument.from_json(json_str)
        
        # Verify equality
        assert restored_doc == original_doc
        assert restored_doc.id == original_doc.id
        assert restored_doc.content == original_doc.content
        assert restored_doc.title == original_doc.title
        assert restored_doc.source == original_doc.source
        assert restored_doc.metadata == original_doc.metadata

    def test_round_trip_with_special_characters(self):
        """Test serialization with special characters and encoding."""
        special_doc = SourceDocument(
            id="special_chars_doc",
            content="Content with special chars: éñ中文🚀\n\t\"quotes\"",
            title="Document with Special Characters: éñ中文🚀",
            source="https://example.com/docs/special-chars?param=value&other=test",
            metadata={"encoding": "utf-8", "special": True}
        )
        
        # Serialize to JSON
        json_str = special_doc.to_json()
        
        # Verify JSON is valid
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        
        # Deserialize from JSON
        restored_doc = SourceDocument.from_json(json_str)
        
        # Verify equality
        assert restored_doc == special_doc

    def test_round_trip_with_empty_and_none_values(self):
        """Test serialization with edge case values."""
        edge_case_doc = SourceDocument(
            id="",
            content="",
            title=None,
            source="",
            metadata=None
        )
        
        # Serialize to JSON
        json_str = edge_case_doc.to_json()
        
        # Deserialize from JSON
        restored_doc = SourceDocument.from_json(json_str)
        
        # Verify equality
        assert restored_doc == edge_case_doc


class TestSourceDocumentEdgeCases:
    """Test SourceDocument edge cases and error handling."""

    def test_very_large_content(self):
        """Test with very large content."""
        large_content = "A" * 100000  # 100KB of content
        
        doc = SourceDocument(
            id="large_doc",
            content=large_content,
            title="Large Document",
            source="https://example.com/large"
        )
        
        assert len(doc.content) == 100000
        assert doc.content == large_content

    def test_unicode_handling(self):
        """Test proper Unicode handling."""
        unicode_doc = SourceDocument(
            id="unicode_test",
            content="Unicode content: 你好世界 🌍 émojis 🚀",
            title="Unicode Title: 测试文档",
            source="https://例え.テスト/文档"
        )
        
        json_str = unicode_doc.to_json()
        restored_doc = SourceDocument.from_json(json_str)
        
        assert restored_doc == unicode_doc
        assert restored_doc.content == "Unicode content: 你好世界 🌍 émojis 🚀"
        assert restored_doc.title == "Unicode Title: 测试文档"

    def test_nested_metadata(self):
        """Test with complex nested metadata."""
        complex_metadata = {
            "document_info": {
                "type": "research_paper",
                "classification": "public",
                "version": 1.2
            },
            "processing": {
                "extracted_at": "2024-01-01T12:00:00Z",
                "extraction_method": "azure_form_recognizer",
                "confidence": 0.95
            },
            "tags": ["AI", "research", "machine learning"],
            "authors": [
                {"name": "John Doe", "affiliation": "University A"},
                {"name": "Jane Smith", "affiliation": "Company B"}
            ]
        }
        
        doc = SourceDocument(
            id="complex_metadata_doc",
            content="Document with complex metadata",
            title="Research Paper",
            source="https://example.com/research",
            metadata=complex_metadata
        )
        
        json_str = doc.to_json()
        restored_doc = SourceDocument.from_json(json_str)
        
        assert restored_doc == doc
        assert restored_doc.metadata == complex_metadata

    def test_metadata_with_none_values(self):
        """Test metadata containing None values."""
        metadata_with_none = {
            "title": "Test",
            "author": None,
            "date": "2024-01-01",
            "version": None,
            "tags": ["test", None, "document"]
        }
        
        doc = SourceDocument(
            id="none_metadata_doc",
            content="Document with None in metadata",
            title="Test Document",
            source="https://example.com/test",
            metadata=metadata_with_none
        )
        
        json_str = doc.to_json()
        restored_doc = SourceDocument.from_json(json_str)
        
        assert restored_doc == doc
        assert restored_doc.metadata == metadata_with_none 