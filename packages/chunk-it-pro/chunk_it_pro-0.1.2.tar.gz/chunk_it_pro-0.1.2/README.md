# ChunkIt Pro - Semantic Document Chunking Library

[![PyPI version](https://badge.fury.io/py/chunk-it-pro.svg)](https://badge.fury.io/py/chunk-it-pro)
[![Python](https://img.shields.io/pypi/pyversions/chunk-it-pro.svg)](https://pypi.org/project/chunk-it-pro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/chunk-it-pro)](https://pepy.tech/project/chunk-it-pro)

Python library for document chunking using semantic analysis. ChunkIt Pro breaks down documents into meaningful segments based on content similarity rather than arbitrary size limits.

## Features

- **Multiple Document Formats**: Supports PDF, DOCX, TXT, MARKDOWN
- **Semantic Analysis**: Uses embedding models to understand content similarity
- **Multiple Embedding Providers**: OpenAI, VoyageAI, and Sentence Transformers support
- **Intelligent Chunking**: Two-pass algorithm for optimal chunk boundaries
- **Configurable Thresholds**: Three methods for similarity threshold computation
- **Visual Analysis**: Generates plots showing similarity patterns
- **Easy Integration**: Simple API for quick integration into existing projects

## Installation

Install from PyPI using pip:

```bash
pip install chunk-it-pro
```

### Development Installation

For development:

```bash
git clone https://github.com/adw777/chunk-it-pro
cd chunk-it-pro
pip install -e .
```

## Quick Start

### Simple Usage (After pip install)

```python
import asyncio
from chunk_it_pro import SemanticChunkingPipeline

async def main():
    # Initialize pipeline
    pipeline = SemanticChunkingPipeline()
    
    # Process document with default settings
    initial_chunks, semantic_chunks, threshold = await pipeline.process_document(
        file_path="your_document.pdf"
    )
    
    print(f"Created {len(semantic_chunks)} semantic chunks")
    for i, chunk in enumerate(semantic_chunks):
        print(f"\nChunk {i+1}: {chunk[:200]}...")

# Run the example
asyncio.run(main())
```

### Convenience Function

```python
import asyncio
from chunk_it_pro.pipeline import chunk_document

async def main():
    # Quick chunking with default settings
    initial_chunks, semantic_chunks, threshold = await chunk_document(
        file_path="document.pdf",
        embedding_provider="voyage"  # or "openai", "axon"
    )
    
    # Use the chunks in your application
    for chunk in semantic_chunks:
        print(f"Chunk length: {len(chunk.split())} words")

asyncio.run(main())
```

## Configuration

### Environment Variables

Set up environment variables (create a `.env` file or set them in your environment):

```env
# Embedding Provider API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
VOYAGEAI_API_KEY=your_voyage_api_key_here

# Optional: Document parsing service
OMNIPARSE_API_URL=https://your-omniparse-url.com/parse_document
```

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Optional* | None |
| `VOYAGEAI_API_KEY` | VoyageAI API key for embeddings | Optional* | None |
| `OMNIPARSE_API_URL` | Omniparse API URL | Optional | Default URL |

*At least one embedding provider API key is required.

### Custom Configuration

You can customize all aspects of the chunking process:

```python
import asyncio
from chunk_it_pro import SemanticChunkingPipeline
from chunk_it_pro.config import Config

async def main():
    # Method 1: Override config globally
    Config.INITIAL_CHUNK_SIZE = 512  # Default: 256 tokens
    Config.MAX_CHUNK_LENGTH = 2048   # Default: 1024 tokens
    Config.MIN_CHUNK_SIZE = 20       # Default: 10 tokens
    Config.DEFAULT_PERCENTILE = 90   # Default: 95
    
    pipeline = SemanticChunkingPipeline()
    
    # Method 2: Pass parameters to process_document
    chunks = await pipeline.process_document(
        file_path="document.pdf",
        threshold_method="gradient",     # Options: "percentile", "gradient", "local_maxima"
        percentile=90,                   # Only used with "percentile" method
        max_chunk_len=2048,              # Override max chunk length
        embedding_provider="openai",     # Options: "openai", "voyage", "axon"
        save_files=True,                 # Save intermediate files
        verbose=True                     # Print progress
    )

asyncio.run(main())
```

## Complete Configuration Reference

### Core Parameters

```python
from chunk_it_pro.config import Config

# Chunking Parameters
Config.INITIAL_CHUNK_SIZE = 256      # Initial chunk size in tokens
Config.MIN_CHUNK_SIZE = 10           # Minimum tokens for valid chunk
Config.MAX_CHUNK_LENGTH = 1024       # Maximum tokens for semantic chunks
Config.DEFAULT_SIMILARITY_THRESHOLD = 0.5  # Fallback similarity threshold

# Threshold Computation
Config.DEFAULT_PERCENTILE = 95       # Percentile for threshold method
Config.THRESHOLD_METHODS = ["percentile", "gradient", "local_maxima"]

# Omniparse URL
OMNIPARSE_API_URL = "http://localhost:8000/parse_document"

# Embedding Models
Config.OPENAI_MODEL = "text-embedding-3-large"
Config.VOYAGE_MODEL = "voyage-law-2"
Config.AXON_MODEL = "axondendriteplus/Legal-Embed-intfloat-multilingual-e5-large-instruct"

# Processing
Config.EMBEDDING_BATCH_SIZE = 100    # Batch size for embedding generation
Config.TOKENIZER_NAME = "cl100k_base"  # Tokenizer for token counting

# Supported file formats
Config.SUPPORTED_FORMATS = {'.pdf', '.txt', '.docx', '.md'}

# Output file names
Config.DEFAULT_OUTPUT_FILES = {
    "initial_chunks": "initial_chunks.txt",
    "semantic_chunks": "semantic_chunks.txt", 
    "embeddings": "embeddings.npy",
    "cosine_plot": "cosine_distances.png"
}
```

### Advanced Usage Examples

#### 1. Custom Chunking with Fine-tuned Parameters

```python
import asyncio
from chunk_it_pro import SemanticChunkingPipeline

async def advanced_chunking():
    pipeline = SemanticChunkingPipeline()
    
    # Fine-tuned parameters for legal documents
    initial_chunks, semantic_chunks, threshold = await pipeline.process_document(
        file_path="legal_document.pdf",
        threshold_method="gradient",      # Better for structured documents
        max_chunk_len=1500,              # Larger chunks for complex content
        embedding_provider="voyage",      # Optimized for legal content
        save_files=True,
        verbose=True
    )
    
    # Get detailed statistics
    stats = pipeline.get_chunk_statistics()
    print(f"Average semantic chunk size: {stats['semantic_chunks']['avg_tokens']:.1f} tokens")
    print(f"Similarity threshold used: {stats['similarity_threshold']:.4f}")

asyncio.run(advanced_chunking())
```

#### 2. Batch Processing Multiple Documents

```python
import asyncio
import os
from chunk_it_pro.pipeline import chunk_document

async def process_directory(directory_path: str):
    results = {}
    
    for filename in os.listdir(directory_path):
        if filename.endswith(('.pdf', '.docx', '.txt', '.md')):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing {filename}...")
            
            try:
                initial, semantic, threshold = await chunk_document(
                    file_path=file_path,
                    embedding_provider="voyage",
                    threshold_method="percentile",
                    percentile=95,
                    max_chunk_len=1024,
                    save_files=False,  # Don't save files for batch processing
                    verbose=False      # Reduce output for batch
                )
                
                results[filename] = {
                    'initial_chunks': len(initial),
                    'semantic_chunks': len(semantic),
                    'threshold': threshold
                }
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                results[filename] = {'error': str(e)}
    
    return results

# Usage
results = asyncio.run(process_directory("./documents"))
for file, data in results.items():
    if 'error' not in data:
        print(f"{file}: {data['semantic_chunks']} chunks (threshold: {data['threshold']:.3f})")
```

#### 3. Custom Configuration Class

```python
import asyncio
from chunk_it_pro import SemanticChunkingPipeline
from chunk_it_pro.chunkers import InitialChunker, SemanticChunker

async def custom_pipeline():
    # Create custom chunkers with specific parameters
    initial_chunker = InitialChunker(
        tokenizer_name="cl100k_base",
        chunk_size=512  # Custom initial chunk size
    )
    
    pipeline = SemanticChunkingPipeline()
    pipeline.initial_chunker = initial_chunker  # Override default
    
    # Process with custom semantic chunker parameters
    initial_chunks, semantic_chunks, threshold = await pipeline.process_document(
        file_path="document.pdf",
        threshold_method="local_maxima",
        max_chunk_len=2048,
        embedding_provider="openai"
    )
    
    return semantic_chunks

chunks = asyncio.run(custom_pipeline())
```

#### 4. Working with Embeddings Directly

```python
import asyncio
import numpy as np
from chunk_it_pro.embeddings import EmbeddingAnalyzer

async def analyze_embeddings():
    analyzer = EmbeddingAnalyzer()
    
    # Custom text chunks
    texts = [
        "This is about machine learning and AI.",
        "Machine learning algorithms are powerful tools.",
        "The weather today is sunny and warm.",
        "Climate change affects weather patterns globally."
    ]
    
    # Generate embeddings
    embeddings = await analyzer.generate_voyage_embeddings(texts)
    analyzer.normalize_embeddings()
    
    # Compute similarities
    distances = analyzer.compute_cosine_distances()
    threshold = analyzer.compute_similarity_threshold(
        distances, 
        method="percentile", 
        percentile=90
    )
    
    print(f"Similarity threshold: {threshold:.4f}")
    print(f"Cosine distances: {distances}")
    
    # Plot similarity pattern
    analyzer.plot_cosine_distances(distances)

asyncio.run(analyze_embeddings())
```

## Embedding Providers

### 1. VoyageAI (Recommended for Legal Documents)
- **Model**: `voyage-law-2`
- **Strengths**: Optimized for legal and structured documents
- **API Key**: Set `VOYAGEAI_API_KEY` environment variable

### 2. OpenAI
- **Model**: `text-embedding-3-large` 
- **Strengths**: High quality general-purpose embeddings
- **API Key**: Set `OPENAI_API_KEY` environment variable

### 3. Axon (Local/Self-hosted)
- **Model**: [Wasserstoff-AI/Legal-Embed-intfloat-multilingual-e5-large-instruct](https://huggingface.co/Wasserstoff-AI/Legal-Embed-intfloat-multilingual-e5-large-instruct)
- **Setup**: Requires sentence-transformers installation

```python
# Use specific provider
chunks = await chunk_document(
    file_path="document.pdf",
    embedding_provider="voyage"  # or "openai" or "axon"
)
```

## Threshold Methods

### 1. Percentile (Default)
Uses the Nth percentile of cosine distances as threshold.

```python
chunks = await pipeline.process_document(
    file_path="document.pdf",
    threshold_method="percentile",
    percentile=95  # Use 95th percentile
)
```

### 2. Gradient
Finds points with highest gradient change in similarity.

```python
chunks = await pipeline.process_document(
    file_path="document.pdf", 
    threshold_method="gradient"
)
```

### 3. Local Maxima
Uses local maxima in distance patterns.

```python
chunks = await pipeline.process_document(
    file_path="document.pdf",
    threshold_method="local_maxima"
)
```

## Output Files

When `save_files=True`, the pipeline creates:

- **`initial_chunks.txt`**: Fixed-size initial chunks (256 tokens each)
- **`semantic_chunks.txt`**: Final semantic chunks  
- **`embeddings.npy`**: Numpy array of embeddings
- **`cosine_distances.png`**: Visualization of similarity patterns

```python
# Control output files
chunks = await pipeline.process_document(
    file_path="document.pdf",
    save_files=True  # Set to False to skip file creation
)
```

## Error Handling

```python
import asyncio
from chunk_it_pro import SemanticChunkingPipeline

async def robust_chunking():
    pipeline = SemanticChunkingPipeline()
    
    try:
        chunks = await pipeline.process_document("document.pdf")
        return chunks
    except FileNotFoundError:
        print("Document file not found")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None, None, None

result = asyncio.run(robust_chunking())
```

## Performance Tips

1. **Batch Processing**: Set `save_files=False` and `verbose=False` for faster batch processing
2. **Embedding Provider**: VoyageAI is generally faster than OpenAI for document chunking
3. **Chunk Size**: Larger initial chunks (512+ tokens) works better for long documents
4. **Local Embeddings Generation**: Use [Wasserstoff-AI/Legal-Embed-intfloat-multilingual-e5-large-instruct](https://huggingface.co/Wasserstoff-AI/Legal-Embed-intfloat-multilingual-e5-large-instruct) to generate embeddings locally

## API Reference

### SemanticChunkingPipeline

```python
class SemanticChunkingPipeline:
    def __init__(self, openai_api_key: str = None, voyage_api_key: str = None)
    
    async def process_document(
        self,
        file_path: str,
        threshold_method: str = "percentile",
        percentile: float = 95,
        max_chunk_len: int = 1024,
        embedding_provider: str = "voyage", 
        save_files: bool = True,
        verbose: bool = True
    ) -> Tuple[List[str], List[str], float]
    
    def get_chunk_statistics(self) -> Dict[str, Any]
    def print_statistics(self) -> None
```

### chunk_document Function

```python
async def chunk_document(
    file_path: str,
    embedding_provider: str = "voyage",
    threshold_method: str = "percentile", 
    percentile: float = 95,
    max_chunk_len: int = 1024,
    save_files: bool = True,
    verbose: bool = True
) -> Tuple[List[str], List[str], float]
```

## Supported File Formats

- **PDF**: `.pdf`
- **Word Documents**: `.docx` 
- **Text Files**: `.txt`
- **Markdown**: `.md`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions:

1. Check the [GitHub Issues](https://github.com/adw777/chunk-it-pro/issues)
2. Create a new issue with detailed description
3. Include sample code and error messages

## Changelog

See [GitHub Releases](https://github.com/adw777/chunk-it-pro/releases) for version history and changes.