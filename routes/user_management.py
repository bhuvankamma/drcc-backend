# routers/users.py

from fastapi import APIRouter, HTTPException
from database.database import get_connection
from schemas.user_management import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# ========================
# Create User
# ========================
@router.post("/")
def create_user(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO add_user (full_name, email, role)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (user.full_name, user.email, user.role)
        )

        new_id = cursor.fetchone()[0]
        conn.commit()

        return {"message": "User created successfully", "id": new_id}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ========================
# Get All Users
# ========================
@router.get("/")
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM add_user ORDER BY id;")
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return result


# ========================
# Update User
# ========================
@router.put("/{id}")
def update_user(id: int, user: UserUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    for key, value in user.dict(exclude_unset=True).items():
        fields.append(f"{key} = %s")
        values.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided")

    values.append(id)

    query = f"""
        UPDATE add_user
        SET {", ".join(fields)}
        WHERE id = %s;
    """

    cursor.execute(query, tuple(values))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.close()
    conn.close()

    return {"message": "User updated successfully"}


# ========================
# Soft Delete
# ========================
@router.delete("/{id}")
def deactivate_user(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE add_user SET status = 'Inactive' WHERE id = %s;",
        (id,)
    )
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.close()
    conn.close()

    return {"message": "User deactivated successfully"}