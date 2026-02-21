# app/routers/admin.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.database import get_db
from models.admin_registration import Admin
from schemas.admin_registration import AdminActionRequest
from crud.admin_registration import (
    hash_password,
    verify_password,
    validate_password_strength,
    PasswordValidationError,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/")
def admin_action(payload: AdminActionRequest, db: Session = Depends(get_db)):
    action = payload.action.lower()

    try:
        # ================= REGISTER =================
        if action == "register":
            if not all([payload.full_name, payload.official_email, payload.password, payload.confirm_password]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing required fields",
                )

            if payload.password != payload.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords do not match",
                )

            try:
                validate_password_strength(payload.password)
            except PasswordValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e.message,
                )

            new_admin = Admin(
                full_name=payload.full_name,
                department=payload.department,
                designation=payload.designation,
                govt_id=payload.govt_id,
                mobile_number=payload.mobile_number,
                official_email=str(payload.official_email),
                password=hash_password(payload.password),
            )

            try:
                db.add(new_admin)
                db.commit()
                db.refresh(new_admin)
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or Govt ID already registered",
                )

            return {"message": "Admin registered successfully"}

        # ================= LOGIN =================
        elif action == "login":

            if not payload.official_email or not payload.password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing email or password",
                )

            admin = db.query(Admin).filter(
                Admin.official_email == str(payload.official_email)
            ).first()

            if not admin or not verify_password(payload.password, admin.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid credentials",
                )

            return {"message": f"Welcome {admin.full_name}!"}

        # ================= REPAIR =================
        elif action == "repair":
            if not payload.official_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email required to identify admin",
                )

            admin = db.query(Admin).filter(
                Admin.official_email == str(payload.official_email)
            ).first()

            is_new_admin = admin is None

            if is_new_admin:
                required_fields = {
                    "full_name": payload.full_name,
                    "department": payload.department,
                    "designation": payload.designation,
                    "govt_id": payload.govt_id,
                    "mobile_number": payload.mobile_number,
                    "password": payload.password,
                    "confirm_password": payload.confirm_password,
                }

                missing_fields = [f for f, v in required_fields.items() if not v]
                if missing_fields:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"For new admin, required fields: {', '.join(missing_fields)}",
                    )

                if payload.password != payload.confirm_password:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Passwords do not match",
                    )

                validate_password_strength(payload.password)

                admin = Admin(
                    full_name=payload.full_name,
                    department=payload.department,
                    designation=payload.designation,
                    govt_id=payload.govt_id,
                    mobile_number=payload.mobile_number,
                    official_email=str(payload.official_email),
                    password=hash_password(payload.password),
                )
                db.add(admin)

            else:
                if payload.full_name:
                    admin.full_name = payload.full_name
                if payload.department:
                    admin.department = payload.department
                if payload.designation:
                    admin.designation = payload.designation
                if payload.mobile_number:
                    admin.mobile_number = payload.mobile_number
                if payload.govt_id:
                    existing = db.query(Admin).filter(
                        Admin.govt_id == payload.govt_id,
                        Admin.id != admin.id
                    ).first()
                    if existing:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Govt ID already registered to another admin",
                        )
                    admin.govt_id = payload.govt_id
                if payload.password:
                    if payload.password != payload.confirm_password:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Passwords do not match",
                        )
                    validate_password_strength(payload.password)
                    admin.password = hash_password(payload.password)

            try:
                db.commit()
                db.refresh(admin)
                action_message = "created" if is_new_admin else "updated"
                return {
                    "message": f"Admin {admin.full_name} {action_message} successfully",
                    "admin_id": admin.id,
                    "action": action_message
                }
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate email or govt ID",
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Valid actions are: register, login, repair",
            )

    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"FastAPI handler error: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )