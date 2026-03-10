import json
from models import CompanyTrack, SessionLocal, init_db

init_db()


def get_session():
    return SessionLocal()


# ---------- CREATE ----------
def create_company_track(
    company_name: str,
    jd: str = None,
    resume_text: str = None,
    resume_filename: str = None,
    ai_response=None,
    status: str = None,
    is_active: bool = True,
):
    db = get_session()
    try:
        ai_str = json.dumps(ai_response) if ai_response and not isinstance(ai_response, str) else ai_response
        record = CompanyTrack(
            company_name=company_name,
            jd=jd,
            resume=resume_text,
            resume_filename=resume_filename,
            ai_response=ai_str,
            status=status,
            is_active=is_active,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    finally:
        db.close()


# ---------- READ ----------
def get_all_company_tracks():
    db = get_session()
    try:
        return db.query(CompanyTrack).order_by(CompanyTrack.created_at.desc()).all()
    finally:
        db.close()


def get_company_track_by_id(record_id: int):
    db = get_session()
    try:
        return db.query(CompanyTrack).filter(CompanyTrack.id == record_id).first()
    finally:
        db.close()


# ---------- UPDATE ----------
def update_company_track(record_id: int, **kwargs):
    db = get_session()
    try:
        record = db.query(CompanyTrack).filter(CompanyTrack.id == record_id).first()
        if not record:
            return False
        if "ai_response" in kwargs and kwargs["ai_response"] and not isinstance(kwargs["ai_response"], str):
            kwargs["ai_response"] = json.dumps(kwargs["ai_response"])
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        db.commit()
        return True
    finally:
        db.close()


# ---------- DELETE (soft) ----------
def toggle_active(record_id: int, is_active: bool):
    db = get_session()
    try:
        record = db.query(CompanyTrack).filter(CompanyTrack.id == record_id).first()
        if record:
            record.is_active = is_active
            db.commit()
            return True
        return False
    finally:
        db.close()