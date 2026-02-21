from typing import Any

import pg8000.dbapi

from models.EmployerRegistration import (
    TABLE_EMPLOYER_REGISTRATION,
    COL_EMPLOYER_ID,
    COL_EMAIL_ADDRESS,
    COL_OTP,
    COL_CONTACT_PERSON_NAME,
    COL_COMPANY_OFFICIAL_NAME,
    COL_PASSWORD,
    COL_IS_VERIFIED,
)


def fetchone_dict(cur) -> dict[str, Any] | None:
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def get_employer_id_by_email(db: pg8000.dbapi.Connection, email: str) -> int | None:
    cur = db.cursor()
    try:
        cur.execute(
            f"SELECT {COL_EMPLOYER_ID} FROM {TABLE_EMPLOYER_REGISTRATION} WHERE {COL_EMAIL_ADDRESS} = %s",
            (email,),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close()


def get_employer_by_email(db: pg8000.dbapi.Connection, email: str) -> dict | None:
    cur = db.cursor()
    try:
        cur.execute(
            f"SELECT {COL_EMPLOYER_ID}, {COL_OTP} FROM {TABLE_EMPLOYER_REGISTRATION} WHERE {COL_EMAIL_ADDRESS} = %s",
            (email,),
        )
        return fetchone_dict(cur)
    finally:
        cur.close()


def create_employer(
    db: pg8000.dbapi.Connection,
    contact_person_name: str,
    company_official_name: str,
    email_address: str,
    hashed_password: str,
    otp: str,
) -> None:
    cur = db.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {TABLE_EMPLOYER_REGISTRATION}
              ({COL_CONTACT_PERSON_NAME}, {COL_COMPANY_OFFICIAL_NAME}, {COL_EMAIL_ADDRESS}, {COL_PASSWORD}, {COL_OTP}, {COL_IS_VERIFIED})
            VALUES
              (%s, %s, %s, %s, %s, %s)
            """,
            (contact_person_name, company_official_name, email_address, hashed_password, otp, False),
        )
    finally:
        cur.close()
    db.commit()


def set_verified_and_clear_otp(db: pg8000.dbapi.Connection, employer_id: int) -> None:
    cur = db.cursor()
    try:
        cur.execute(
            f"""
            UPDATE {TABLE_EMPLOYER_REGISTRATION}
            SET {COL_IS_VERIFIED} = %s, {COL_OTP} = %s
            WHERE {COL_EMPLOYER_ID} = %s
            """,
            (True, None, employer_id),
        )
    finally:
        cur.close()
    db.commit()


def update_otp(db: pg8000.dbapi.Connection, employer_id: int, otp: str) -> None:
    cur = db.cursor()
    try:
        cur.execute(
            f"UPDATE {TABLE_EMPLOYER_REGISTRATION} SET {COL_OTP} = %s WHERE {COL_EMPLOYER_ID} = %s",
            (otp, employer_id),
        )
    finally:
        cur.close()
    db.commit()


def update_password_and_clear_otp(
    db: pg8000.dbapi.Connection, employer_id: int, hashed_password: str
) -> None:
    cur = db.cursor()
    try:
        cur.execute(
            f"""
            UPDATE {TABLE_EMPLOYER_REGISTRATION}
            SET {COL_PASSWORD} = %s, {COL_OTP} = %s
            WHERE {COL_EMPLOYER_ID} = %s
            """,
            (hashed_password, None, employer_id),
        )
    finally:
        cur.close()
    db.commit()
