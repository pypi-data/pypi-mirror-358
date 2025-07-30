"""
Kallia - Semantic Document Processing Library

Kallia is a FastAPI-based document processing service that converts documents into
intelligent semantic chunks. The library specializes in extracting meaningful content
segments from documents while preserving context and semantic relationships.

Key Features:
- Document-to-markdown conversion for standardized processing
- Semantic chunking that respects document structure and meaning
- Support for PDF documents with extensible architecture for additional formats
- RESTful API interface with comprehensive error handling
- Configurable processing parameters (temperature, token limits, page selection)

The library is designed for applications requiring document analysis, content
extraction, knowledge base construction, and semantic search implementations.

Author: CK
GitHub: https://github.com/kallia-project/kallia
License: Apache License 2.0
Version: 0.1.0
"""

import requests
import logging
import kallia.models as Models
import kallia.constants as Constants
from fastapi import FastAPI, HTTPException
from kallia.exceptions import InvalidParametersException
from kallia.documents import Documents
from kallia.chunker import Chunker
from kallia.logger import Logger
from kallia.utils import Utils

logger = logging.getLogger(__name__)
Logger.config(logger)

app = FastAPI(title=Constants.APP_NAME, version=Constants.VERSION)


@app.post("/chunks", response_model=Models.ChunksResponse)
def chunks(request: Models.ChunksRequest):
    try:
        file_format = Utils.get_extension(request.url)
        if file_format not in Constants.SUPPORTED_FILE_FORMATS:
            raise InvalidParametersException(f"Unsupported file format: {file_format}")
        markdown_content = Documents.to_markdown(
            source=request.url,
            page_number=request.page_number,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        semantic_chunks = Chunker.create(
            text=markdown_content,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return Models.ChunksResponse(chunks=semantic_chunks)

    except requests.exceptions.RequestException as e:
        logger.error(f"Service Unavailable {request.url} {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

    except InvalidParametersException as e:
        logger.error(f"Invalid Parameters {request.url} {e}")
        raise HTTPException(status_code=400, detail="Invalid Parameters")

    except Exception as e:
        logger.error(f"Internal Server Error {request.url} {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
