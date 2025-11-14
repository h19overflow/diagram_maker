# Semantic Chunking Implementation Summary

## Changes Made

• Replaced `TokenTextSplitter` with `SemanticChunker` from `langchain_experimental.text_splitter`
• Added `BedrockEmbeddings` initialization in `_build_text_splitter()` function
• Configured `SemanticChunker` with 80th percentile breakpoint threshold
• Used `breakpoint_threshold_type="percentile"` and `breakpoint_threshold_amount=80.0`
• Maintained same interface - `chunk_documents()` function signature unchanged
• Preserved `_merge_small_chunks()` functionality for minimum token size enforcement
• Updated logging messages to reflect semantic chunking approach
• Added `langchain-experimental==0.4.0` to `requirements.txt` (compatible with langchain-core 1.0.4)
• Kept all existing metadata handling and token counting utilities

## Implementation Details

• Semantic chunking uses embedding similarity to determine natural breakpoints
• 80th percentile threshold means splits occur at top 20% of semantic differences
• Bedrock embeddings model configured from `RAGConfig` (Titan v2 by default)
• Minimum chunk size validation and merging logic remains intact
• Progress tracking with tqdm preserved for user feedback

## Files Modified

• `src/core/pipeline/chunking.py` - Main implementation changes
• `requirements.txt` - Added langchain-experimental dependency

