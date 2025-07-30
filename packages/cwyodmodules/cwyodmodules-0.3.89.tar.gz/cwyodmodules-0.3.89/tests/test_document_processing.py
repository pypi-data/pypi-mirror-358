"""
Tests for document processing modules.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from cwyodmodules.batch.utilities.document_loading.document_loading_base import DocumentLoadingBase
from cwyodmodules.batch.utilities.document_chunking.chunking_strategy import ChunkingStrategy
from cwyodmodules.batch.utilities.document_chunking.document_chunking_base import DocumentChunkingBase


class TestDocumentLoadingBase:
    """Test document loading base functionality."""

    def test_document_loading_base_cannot_be_instantiated(self):
        """Test that DocumentLoadingBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DocumentLoadingBase()

    def test_document_loading_base_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        class TestLoader(DocumentLoadingBase):
            pass
        
        with pytest.raises(TypeError):
            TestLoader()


class TestChunkingStrategy:
    """Test document chunking strategy."""

    def test_chunking_strategy_page_based(self):
        """Test page-based chunking strategy."""
        strategy = ChunkingStrategy.PAGE_BASED
        assert strategy.value == "page_based"

    def test_chunking_strategy_token_based(self):
        """Test token-based chunking strategy.""" 
        strategy = ChunkingStrategy.TOKEN_BASED
        assert strategy.value == "token_based"

    def test_chunking_strategy_semantic_based(self):
        """Test semantic-based chunking strategy."""
        strategy = ChunkingStrategy.SEMANTIC_BASED
        assert strategy.value == "semantic_based"


class TestDocumentChunkingBase:
    """Test document chunking base functionality."""

    def test_document_chunking_base_cannot_be_instantiated(self):
        """Test that DocumentChunkingBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DocumentChunkingBase()

    def test_document_chunking_base_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        class TestChunker(DocumentChunkingBase):
            pass
        
        with pytest.raises(TypeError):
            TestChunker()


class TestWebDocumentLoader:
    """Test web document loader."""

    @patch('cwyodmodules.batch.utilities.document_loading.web.logger')
    def test_web_loader_initialization(self, mock_logger):
        """Test web document loader initialization."""
        from cwyodmodules.batch.utilities.document_loading.web import WebDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        loader = WebDocumentLoader()
        assert loader is not None

    @patch('cwyodmodules.batch.utilities.document_loading.web.requests')
    @patch('cwyodmodules.batch.utilities.document_loading.web.logger')
    def test_web_loader_load_success(self, mock_logger, mock_requests):
        """Test successful web document loading."""
        from cwyodmodules.batch.utilities.document_loading.web import WebDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_requests.get.return_value = mock_response
        
        loader = WebDocumentLoader()
        result = loader.load("https://example.com/test")
        
        assert "Test content" in result
        mock_requests.get.assert_called_once_with("https://example.com/test")

    @patch('cwyodmodules.batch.utilities.document_loading.web.requests')
    @patch('cwyodmodules.batch.utilities.document_loading.web.logger')
    def test_web_loader_load_failure(self, mock_logger, mock_requests):
        """Test web document loading failure."""
        from cwyodmodules.batch.utilities.document_loading.web import WebDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        loader = WebDocumentLoader()
        
        with pytest.raises(Exception):
            loader.load("https://example.com/notfound")
        
        mock_logger.exception.assert_called()


class TestWordDocumentLoader:
    """Test Word document loader."""

    @patch('cwyodmodules.batch.utilities.document_loading.word_document.logger')
    def test_word_loader_initialization(self, mock_logger):
        """Test Word document loader initialization."""
        from cwyodmodules.batch.utilities.document_loading.word_document import WordDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        loader = WordDocumentLoader()
        assert loader is not None

    @patch('cwyodmodules.batch.utilities.document_loading.word_document.Document')
    @patch('cwyodmodules.batch.utilities.document_loading.word_document.logger')
    def test_word_loader_load_success(self, mock_logger, mock_document):
        """Test successful Word document loading."""
        from cwyodmodules.batch.utilities.document_loading.word_document import WordDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Mock document paragraphs
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "Second paragraph"
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document.return_value = mock_doc
        
        loader = WordDocumentLoader()
        result = loader.load(b"mock docx content")
        
        assert "First paragraph" in result
        assert "Second paragraph" in result
        mock_document.assert_called_once()

    @patch('cwyodmodules.batch.utilities.document_loading.word_document.Document')
    @patch('cwyodmodules.batch.utilities.document_loading.word_document.logger')
    def test_word_loader_load_exception(self, mock_logger, mock_document):
        """Test Word document loading with exception."""
        from cwyodmodules.batch.utilities.document_loading.word_document import WordDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        mock_document.side_effect = Exception("Invalid document")
        
        loader = WordDocumentLoader()
        
        with pytest.raises(Exception, match="Invalid document"):
            loader.load(b"invalid content")
        
        mock_logger.exception.assert_called()


class TestReadDocumentLoader:
    """Test read document loader."""

    @patch('cwyodmodules.batch.utilities.document_loading.read.logger')
    def test_read_loader_initialization(self, mock_logger):
        """Test read document loader initialization."""
        from cwyodmodules.batch.utilities.document_loading.read import ReadDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        loader = ReadDocumentLoader()
        assert loader is not None

    @patch('cwyodmodules.batch.utilities.document_loading.read.logger')
    def test_read_loader_load_text_success(self, mock_logger):
        """Test successful text document loading."""
        from cwyodmodules.batch.utilities.document_loading.read import ReadDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        loader = ReadDocumentLoader()
        text_content = "This is test text content"
        result = loader.load(text_content.encode('utf-8'))
        
        assert result == text_content

    @patch('cwyodmodules.batch.utilities.document_loading.read.logger')
    def test_read_loader_load_encoding_error(self, mock_logger):
        """Test text document loading with encoding error."""
        from cwyodmodules.batch.utilities.document_loading.read import ReadDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.warning = Mock()
        
        loader = ReadDocumentLoader()
        # Test with invalid UTF-8 bytes
        invalid_bytes = b'\x80\x81\x82\x83'
        result = loader.load(invalid_bytes)
        
        # Should handle encoding gracefully
        assert isinstance(result, str)
        mock_logger.warning.assert_called()


class TestTokenBasedChunker:
    """Test token-based document chunker."""

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_token_chunker_initialization(self, mock_logger):
        """Test token-based chunker initialization."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = TokenBasedChunker(chunk_size=100, overlap=20)
        assert chunker.chunk_size == 100
        assert chunker.overlap == 20

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_token_chunker_chunk_text(self, mock_logger):
        """Test text chunking functionality."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = TokenBasedChunker(chunk_size=10, overlap=2)
        
        # Create text with more than 10 tokens
        text = "This is a test document with many words that should be chunked into smaller pieces for processing."
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk.split()) <= 12 for chunk in chunks)  # chunk_size + overlap

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_token_chunker_empty_text(self, mock_logger):
        """Test chunking empty text."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = TokenBasedChunker(chunk_size=100, overlap=20)
        chunks = chunker.chunk("")
        
        assert chunks == []

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_token_chunker_short_text(self, mock_logger):
        """Test chunking text shorter than chunk size."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = TokenBasedChunker(chunk_size=100, overlap=20)
        text = "Short text"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text


class TestPageBasedChunker:
    """Test page-based document chunker."""

    @patch('cwyodmodules.batch.utilities.document_chunking.page_based_chunker.logger')
    def test_page_chunker_initialization(self, mock_logger):
        """Test page-based chunker initialization."""
        from cwyodmodules.batch.utilities.document_chunking.page_based_chunker import PageBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = PageBasedChunker()
        assert chunker is not None

    @patch('cwyodmodules.batch.utilities.document_chunking.page_based_chunker.logger')
    def test_page_chunker_chunk_by_delimiter(self, mock_logger):
        """Test page-based chunking by delimiter."""
        from cwyodmodules.batch.utilities.document_chunking.page_based_chunker import PageBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = PageBasedChunker()
        
        # Text with page break delimiter
        text = "Page 1 content\n\f\nPage 2 content\n\f\nPage 3 content"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3
        assert "Page 1 content" in chunks[0]
        assert "Page 2 content" in chunks[1]
        assert "Page 3 content" in chunks[2]

    @patch('cwyodmodules.batch.utilities.document_chunking.page_based_chunker.logger')
    def test_page_chunker_no_delimiter(self, mock_logger):
        """Test page-based chunking without delimiter."""
        from cwyodmodules.batch.utilities.document_chunking.page_based_chunker import PageBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        chunker = PageBasedChunker()
        text = "Single page content without page breaks"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text


class TestIntegrationScenarios:
    """Test integration scenarios for document processing."""

    @patch('cwyodmodules.batch.utilities.document_loading.web.requests')
    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    @patch('cwyodmodules.batch.utilities.document_loading.web.logger')
    def test_web_to_chunking_pipeline(self, mock_web_logger, mock_chunker_logger, mock_requests):
        """Test complete pipeline from web loading to chunking."""
        from cwyodmodules.batch.utilities.document_loading.web import WebDocumentLoader
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_web_logger.trace_function = lambda **kwargs: lambda func: func
        mock_chunker_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Mock web response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
        <body>
        <p>This is a long document with multiple paragraphs.</p>
        <p>It contains various sections that need to be processed.</p>
        <p>The content should be chunked into smaller pieces for better handling.</p>
        <p>Each chunk should maintain context while being manageable in size.</p>
        </body>
        </html>
        """
        mock_requests.get.return_value = mock_response
        
        # Load document from web
        loader = WebDocumentLoader()
        content = loader.load("https://example.com/document")
        
        # Chunk the content
        chunker = TokenBasedChunker(chunk_size=15, overlap=3)
        chunks = chunker.chunk(content)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Verify content is preserved across chunks
        combined_content = " ".join(chunks)
        assert "long document" in combined_content
        assert "multiple paragraphs" in combined_content

    @patch('cwyodmodules.batch.utilities.document_loading.word_document.Document')
    @patch('cwyodmodules.batch.utilities.document_chunking.page_based_chunker.logger')
    @patch('cwyodmodules.batch.utilities.document_loading.word_document.logger')
    def test_word_to_page_chunking_pipeline(self, mock_word_logger, mock_chunker_logger, mock_document):
        """Test pipeline from Word document loading to page-based chunking."""
        from cwyodmodules.batch.utilities.document_loading.word_document import WordDocumentLoader
        from cwyodmodules.batch.utilities.document_chunking.page_based_chunker import PageBasedChunker
        
        mock_word_logger.trace_function = lambda **kwargs: lambda func: func
        mock_chunker_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Mock Word document with page breaks
        mock_paragraphs = []
        page_1_content = ["First page paragraph 1", "First page paragraph 2"]
        page_2_content = ["Second page paragraph 1", "Second page paragraph 2"]
        
        for content in page_1_content:
            mock_para = Mock()
            mock_para.text = content
            mock_paragraphs.append(mock_para)
        
        # Add page break indicator
        mock_para_break = Mock()
        mock_para_break.text = "\f"
        mock_paragraphs.append(mock_para_break)
        
        for content in page_2_content:
            mock_para = Mock()
            mock_para.text = content
            mock_paragraphs.append(mock_para)
        
        mock_doc = Mock()
        mock_doc.paragraphs = mock_paragraphs
        mock_document.return_value = mock_doc
        
        # Load Word document
        loader = WordDocumentLoader()
        content = loader.load(b"mock docx content")
        
        # Chunk by pages
        chunker = PageBasedChunker()
        chunks = chunker.chunk(content)
        
        assert len(chunks) >= 2
        assert "First page paragraph 1" in chunks[0]
        assert "Second page paragraph 1" in chunks[1]


class TestErrorHandling:
    """Test error handling in document processing."""

    @patch('cwyodmodules.batch.utilities.document_loading.web.requests')
    @patch('cwyodmodules.batch.utilities.document_loading.web.logger')
    def test_web_loader_network_error(self, mock_logger, mock_requests):
        """Test web loader network error handling."""
        from cwyodmodules.batch.utilities.document_loading.web import WebDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        mock_requests.get.side_effect = Exception("Network error")
        
        loader = WebDocumentLoader()
        
        with pytest.raises(Exception, match="Network error"):
            loader.load("https://example.com/document")
        
        mock_logger.exception.assert_called()

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_token_chunker_invalid_parameters(self, mock_logger):
        """Test token chunker with invalid parameters."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Test with invalid chunk size
        with pytest.raises(ValueError):
            TokenBasedChunker(chunk_size=0)
        
        # Test with negative overlap
        with pytest.raises(ValueError):
            TokenBasedChunker(chunk_size=100, overlap=-1)
        
        # Test with overlap larger than chunk size
        with pytest.raises(ValueError):
            TokenBasedChunker(chunk_size=10, overlap=15)

    @patch('cwyodmodules.batch.utilities.document_loading.read.logger')
    def test_read_loader_none_content(self, mock_logger):
        """Test read loader with None content."""
        from cwyodmodules.batch.utilities.document_loading.read import ReadDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.warning = Mock()
        
        loader = ReadDocumentLoader()
        
        with pytest.raises(AttributeError):
            loader.load(None)


class TestPerformanceScenarios:
    """Test performance-related scenarios."""

    @patch('cwyodmodules.batch.utilities.document_chunking.token_based_chunker.logger')
    def test_large_document_chunking(self, mock_logger):
        """Test chunking of large documents."""
        from cwyodmodules.batch.utilities.document_chunking.token_based_chunker import TokenBasedChunker
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Create a large document (simulated)
        large_text = " ".join(["word"] * 10000)  # 10,000 words
        
        chunker = TokenBasedChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(large_text)
        
        # Verify chunking worked
        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 550 for chunk in chunks)  # chunk_size + overlap
        
        # Verify no content is lost
        total_words = sum(len(chunk.split()) for chunk in chunks)
        # Should be greater than original due to overlap
        assert total_words >= 10000

    @patch('cwyodmodules.batch.utilities.document_loading.read.logger')
    def test_large_text_loading(self, mock_logger):
        """Test loading of large text documents."""
        from cwyodmodules.batch.utilities.document_loading.read import ReadDocumentLoader
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Create large text content
        large_content = "A" * 1000000  # 1MB of text
        
        loader = ReadDocumentLoader()
        result = loader.load(large_content.encode('utf-8'))
        
        assert len(result) == 1000000
        assert result == large_content 