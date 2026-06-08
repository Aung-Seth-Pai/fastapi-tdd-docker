# backend/app/api/summaries.py

from fastapi import APIRouter, HTTPException

from app.api import crud
from app.models.pydantic import SummaryPayloadSchema, SummaryResponseSchema, SummaryUpdatePayloadSchema  # isort:skip
from app.models.text_summary import SummarySchema

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema) -> SummaryResponseSchema:
    summary_id = await crud.post(payload)
    response_object = {
        "id": summary_id,
        "url": payload.url,
    }
    return response_object


@router.get("/summarize/{summary_id}", response_model=SummarySchema)
async def read_summary(summary_id: int) -> SummarySchema:
    summary = await crud.get(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/summarize", response_model=list[SummarySchema])
async def read_all_summaries() -> list[SummarySchema]:
    summaries = await crud.get_all()
    return summaries


@router.delete("/summarize/{summary_id}", response_model=SummaryResponseSchema)
async def delete_summary(summary_id: int) -> SummaryResponseSchema:
    deleted_summary = await crud.delete(summary_id)
    if not deleted_summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return deleted_summary


@router.put("/summarize/{summary_id}", response_model=SummarySchema)
async def update_summary(summary_id: int, payload: SummaryUpdatePayloadSchema) -> SummarySchema:
    updated_summary = await crud.put(summary_id, payload)
    if not updated_summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return updated_summary
