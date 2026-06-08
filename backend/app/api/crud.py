# backend/app/api/crud.py

from typing import List, Union

from app.models.pydantic import SummaryPayloadSchema, SummaryUpdatePayloadSchema
from app.models.text_summary import TextSummary


async def post(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(url=payload.url, summary="dummy summary")
    await summary.save()
    return summary.id


async def get(summary_id: int) -> Union[dict, None]:
    summary = await TextSummary.filter(id=summary_id).first().values()
    if summary:
        return summary
    return None


async def get_all() -> List:
    summaries = await TextSummary.all().values()
    return summaries


async def delete(summary_id: int) -> Union[dict, None]:
    summary = await TextSummary.filter(id=summary_id).first()
    if summary:
        await summary.delete()
        return {"id": summary_id, "url": summary.url}
    return None


async def put(summary_id: int, payload: SummaryUpdatePayloadSchema) -> Union[dict, None]:
    summary = await TextSummary.filter(id=summary_id).update(url=payload.url, summary=payload.summary)
    if summary:
        return await TextSummary.filter(id=summary_id).first().values()
    return None
