import os
import requests
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RAGMetadata:
    """Metadata for RAG search results."""
    doc_id: str  # Knowledge base document ID
    created_at: str  # Creation timestamp
    base_id: str  # Knowledge base ID
    keyword: List[str]  # Content keywords


@dataclass
class RAGContext:
    """Represents a single RAG search result context."""
    page_content: str  # Content text
    metadata: RAGMetadata  # Associated metadata
    id: str  # Context ID
    score: float  # Similarity score
    word_counts: int  # Word count
    retrieval_counts: int  # Number of times retrieved
    source_file_name: str  # Source file name
    source_file_path: List[str]  # Source file path


def rag_search(
    base_id: str,
    text: str,
    topK: int = 5,
    score_threshold: float = 0.3,
    host: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False
) -> List[RAGContext]:
    """
    Perform a RAG (Retrieval-Augmented Generation) search against a knowledge base.
    
    Args:
        base_id: ID of the knowledge base to search
        text: Query text to search for
        topK: Maximum number of results to return (default: 5)
        score_threshold: Minimum similarity score threshold (default: 0.3)
        host: API host URL (default: from HEYWHALE_HOST environment variable)
        token: Authentication token (default: from MW_TOKEN environment variable)
        debug: Whether to print debug information (default: False)
        
    Returns:
        List of RAGContext objects containing search results
        
    Raises:
        ValueError: If required parameters are missing
        requests.RequestException: For network-related errors
    """
    # Validate required parameters
    if not base_id:
        raise ValueError("base_id is required")
    if not text:
        raise ValueError("text is required")
    
    # Get host and token from environment if not provided
    host = host or os.getenv("HEYWHALE_HOST")
    if not host:
        raise ValueError("Host must be provided or set as HEYWHALE_HOST environment variable")
    
    token = token or os.getenv("MW_TOKEN")
    if not token:
        raise ValueError("Token must be provided or set as MW_TOKEN environment variable")
    
    # Make sure float score_threshold between [0,1]
    if not 0 <= score_threshold <= 1:
        raise ValueError("score_threshold must be between 0 and 1")
    # Make sure topK is a positive integer [1, 100]
    if not 1 <= topK <= 100:
        raise ValueError("topK must be a positive integer between 1 and 100")
    
    # Construct API endpoint
    base_url = f"{host}/api/org/member/rag/search"
    
    headers = {
        "Content-Type": "application/json",
        "x-kesci-token": token,
    }
    
    params = {
        "base_id": base_id,
        "text": text,
        "topK": topK,
        "score_threshold": score_threshold,
    }
    
    try:
        if debug:
            print(f"Requesting {base_url} with params: {params}")
        
        response = requests.get(
            base_url, 
            headers=headers, 
            params=params, 
            timeout=60
        )
        
        response.raise_for_status()  # Raise exception for non-200 responses
        
        results = []
        data = response.json()
        
        for item in data:
            metadata = RAGMetadata(
                doc_id=item["metadata"]["doc_id"],
                created_at=item["metadata"]["created_at"],
                base_id=item["metadata"]["base_id"],
                keyword=item["metadata"]["keyword"],
            )
            
            context = RAGContext(
                page_content=item["page_content"],
                metadata=metadata,
                id=item["id"],
                score=item["score"],
                word_counts=item["word_counts"],
                retrieval_counts=item["retrieval_counts"],
                source_file_name=item["source_file_name"],
                source_file_path=item["source_file_path"],
            )
            
            results.append(context)
            
        return results
        
    except requests.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else "unknown"
        error_text = e.response.text if hasattr(e, 'response') else str(e)
        if debug:
            print(f"HTTP error occurred (status code {status_code}): {error_text}")
        raise
        
    except requests.RequestException as e:
        if debug:
            print(f"Network error occurred: {e}")
        raise