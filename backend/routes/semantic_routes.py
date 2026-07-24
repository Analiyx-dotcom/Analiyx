"""Routes for semantic search and business glossary."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from auth import get_verified_user_id
from services.semantic.search import SemanticSearch
from services.semantic.glossary import BusinessGlossary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/semantic", tags=["semantic"])

db = None


def set_database(database):
    global db
    db = database


class SearchRequest(BaseModel):
    datasource_id: str
    query: str
    limit: int = 10


class GlossaryCreateRequest(BaseModel):
    term: str
    definition: str
    synonyms: str = ""
    related_tables: List[str] = []
    related_columns: List[str] = []


class GlossaryUpdateRequest(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    synonyms: Optional[str] = None
    related_tables: Optional[List[str]] = None
    related_columns: Optional[List[str]] = None


@router.post("/search")
async def semantic_search(req: SearchRequest, user_id: str = Depends(get_verified_user_id)):
    try:
        search = SemanticSearch(db)
        results = await search.search(req.datasource_id, user_id, req.query, req.limit)
        return results
    except Exception as e:
        logger.error("Semantic search failed: %s", e)
        raise HTTPException(500, f"Search failed: {e}")


@router.post("/glossary")
async def create_glossary_term(req: GlossaryCreateRequest, user_id: str = Depends(get_verified_user_id)):
    glossary = BusinessGlossary(db)
    term = await glossary.add_term(
        user_id=user_id,
        term=req.term,
        definition=req.definition,
        synonyms=req.synonyms,
        related_tables=req.related_tables,
        related_columns=req.related_columns,
    )
    return term


@router.get("/glossary")
async def list_glossary_terms(search: str = "", user_id: str = Depends(get_verified_user_id)):
    glossary = BusinessGlossary(db)
    terms = await glossary.list_terms(user_id, search)
    return {"terms": terms, "count": len(terms)}


@router.get("/glossary/{term_id}")
async def get_glossary_term(term_id: str, user_id: str = Depends(get_verified_user_id)):
    glossary = BusinessGlossary(db)
    term = await glossary.get_term(term_id, user_id)
    if not term:
        raise HTTPException(404, "Term not found")
    return term


@router.put("/glossary/{term_id}")
async def update_glossary_term(term_id: str, req: GlossaryUpdateRequest,
                                user_id: str = Depends(get_verified_user_id)):
    glossary = BusinessGlossary(db)
    try:
        updates = req.model_dump(exclude_none=True)
        term = await glossary.update_term(term_id, user_id, updates)
        return term
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/glossary/{term_id}")
async def delete_glossary_term(term_id: str, user_id: str = Depends(get_verified_user_id)):
    glossary = BusinessGlossary(db)
    deleted = await glossary.delete_term(term_id, user_id)
    if not deleted:
        raise HTTPException(404, "Term not found")
    return {"success": True}
