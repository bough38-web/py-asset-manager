from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import database

# DB 초기화
database.init_db()

app = FastAPI(title="기업 자산관리 API", description="FastAPI + SQLite")

# === 데이터 검증 모델 (Pydantic) ===
class AssetCreate(BaseModel):
    asset_code: str
    name: str
    category: str
    owner: str
    purchase_date: date
    price: int

class AssetResponse(AssetCreate):
    id: int
    status: str
    class Config:
        from_attributes = True

# === DB 세션 의존성 ===
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === API 엔드포인트 ===

# 1. 자산 등록
@app.post("/assets/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = database.Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

# 2. 전체 자산 조회
@app.get("/assets/", response_model=List[AssetResponse])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assets = db.query(database.Asset).offset(skip).limit(limit).all()
    return assets

# 3. 자산 상태 업데이트 (수리/폐기 등)
@app.put("/assets/{asset_id}/status")
def update_status(asset_id: int, status: str, db: Session = Depends(get_db)):
    asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.status = status
    
    # 반납(퇴사), 폐기, 매각, 분실, 보관중 시 사용자 정보 초기화 로직
    if status in ["반납(퇴사)", "폐기", "매각", "분실", "보관중"]:
        asset.owner = ""  # 소유자 정보 제거
        
    db.commit()
    return {"msg": "Status updated", "new_status": status, "owner": asset.owner}

# 4. 자산 정보 전체 수정 (수정 기능)
@app.put("/assets/{asset_id}")
def update_asset(asset_id: int, asset_data: AssetCreate, db: Session = Depends(get_db)):
    asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Pydantic 모델에서 값 복사 (id 제외)
    asset.asset_code = asset_data.asset_code
    asset.name = asset_data.name
    asset.category = asset_data.category
    asset.owner = asset_data.owner
    asset.purchase_date = asset_data.purchase_date
    asset.price = asset_data.price
    
    db.commit()
    db.refresh(asset)
    return asset

# 5. 자산 삭제
@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(database.Asset).filter(database.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    return {"msg": "Asset deleted"}