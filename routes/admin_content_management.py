from fastapi import APIRouter, HTTPException
import models.admin_content_management

router = APIRouter()


def format_response(row):
    if not row:
        return None
    return {
        "id": row[0],
        "title": row[1],
        "type": row[2],
        "content": row[3],
        "updated_at": row[4],
    }


# ✅ GET ALL CONTENT
@router.get("/content")
def get_content_list():
    rows = models.admin_content_management.get_all_content()
    return [format_response(row) for row in rows]


# ✅ GET SINGLE CONTENT
@router.get("/content/{content_id}")
def get_single_content(content_id: int):
    row = models.admin_content_management.get_content_by_id(content_id)
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    return format_response(row)


# ✅ UPDATE CONTENT
@router.put("/content/{content_id}")
def update_content(content_id: int, payload: dict):
    updated = models.admin_content_management.update_content(content_id, payload["content"])
    if not updated:
        raise HTTPException(status_code=404, detail="Content not found")
    return format_response(updated)