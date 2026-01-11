from sqlalchemy.orm import Session
from database import SessionLocal, Asset, init_db, engine
import random
from datetime import date, timedelta

# DB 초기화 ensure tables exist
init_db()

db: Session = SessionLocal()

# 기존 데이터 삭제 (Clean state for "force apply")
db.query(Asset).delete()
db.commit()

# 데이터 생성 함수
def create_random_assets():
    # 데이터셋 정의
    departments = ["영업1팀", "영업2팀", "기획팀", "개발1팀", "개발2팀", "인사팀", "재무팀", "디자인팀"]
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신"]
    first_names = ["철수", "영희", "민수", "지영", "동현", "현우", "서준", "지민", "민지", "예진", "준호", "성민", "수빈"]
    
    asset_types = {
        "IT기기": [
            ("MacBook Pro 16 M3", 3500000), ("MacBook Air 15 M2", 2000000), 
            ("Dell XPS 15", 2800000), ("LG Gram 17", 1900000), 
            ("Samsung Galaxy Book 3", 1800000), ("iPad Pro 12.9", 1700000),
            ("Dell UltraSharp Monitor 27", 600000), ("LG UltraFine 32", 900000)
        ],
        "가구": [
            ("퍼시스 모션데스크", 800000), ("시디즈 T50 의자", 350000), 
            ("허먼밀러 에어론", 1800000), ("3단 서랍장", 150000), ("회의용 테이블", 600000)
        ],
        "소프트웨어": [
            ("Adobe CC All Apps", 700000), ("JetBrains All Products", 400000), 
            ("Microsoft 365 Business", 200000), ("Sketch License", 120000)
        ],
        "차량": [
            ("제네시스 G80 (법인)", 60000000), ("아반떼 cn7 (영업용)", 25000000), 
            ("카니발 하이리무진", 45000000)
        ],
        "기타": [
            ("네스프레소 커피머신", 250000), ("LG 퓨리케어 공기청정기", 800000), 
            ("삼성 비스포크 냉장고", 1500000), ("다이슨 청소기", 900000)
        ]
    }
    
    statuses = ["정상", "정상", "정상", "정상", "정상", "정상", "수리중", "반납(퇴사)", "폐기", "매각", "분실"]
    
    assets_to_add = []
    
    code_counters = {"IT기기": 1, "가구": 1, "소프트웨어": 1, "차량": 1, "기타": 1}
    category_codes = {"IT기기": "IT", "가구": "FUR", "소프트웨어": "SW", "차량": "CAR", "기타": "ETC"}

    for _ in range(80): # 80개 아이템 생성
        category = random.choice(list(asset_types.keys()))
        item_name, base_price = random.choice(asset_types[category])
        
        # 가격 변동 (±10%)
        price = int(base_price * random.uniform(0.9, 1.1) / 1000) * 1000
        
        status = random.choice(statuses)
        
        owner = ""
        # 소유자가 필요한 상태인 경우 랜덤 생성
        if status in ["정상", "수리중"]:
             dept = random.choice(departments)
             name = random.choice(last_names) + random.choice(first_names)
             owner = f"{dept} {name}"
        
        # 구매일: 최근 3년 이내
        days_offset = random.randint(0, 365 * 3)
        purchase_date = date.today() - timedelta(days=days_offset)
        
        # 자산코드 생성 (예: IT-23001)
        year_suffix = purchase_date.year % 100
        seq = code_counters[category]
        asset_code = f"{category_codes[category]}-{year_suffix}{seq:03d}"
        code_counters[category] += 1
        
        asset = Asset(
            asset_code=asset_code,
            name=item_name,
            category=category,
            status=status,
            owner=owner,
            purchase_date=purchase_date,
            price=price
        )
        assets_to_add.append(asset)
        
    db.add_all(assets_to_add)
    db.commit()
    print(f"Successfully added {len(assets_to_add)} random assets.")

if __name__ == "__main__":
    try:
        create_random_assets()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
