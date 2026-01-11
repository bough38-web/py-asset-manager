from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 운영 시에는 PostgreSQL URL로 변경 (예: postgresql://user:pass@localhost/db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./assets.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === 자산 테이블 모델 ===
class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String, unique=True, index=True) # 자산관리번호 (예: IT-23001)
    name = Column(String, index=True)       # 자산명 (예: Macbook Pro M3)
    category = Column(String)               # 분류 (IT기기, 가구, 차량)
    status = Column(String, default="정상")  # 상태 (정상, 수리중, 폐기, 분실)
    owner = Column(String, nullable=True)   # 현재 사용자 (지사/담당자명)
    purchase_date = Column(Date)            # 구매일
    price = Column(Integer)                 # 가격
    created_at = Column(DateTime, default=datetime.now)

# 테이블 생성 함수
def init_db():
    Base.metadata.create_all(bind=engine)