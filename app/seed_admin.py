import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal  
from app.model.user import User  

# --- ADD THESE MISSING IMPORTS ---
# (Adjust the 'app.model.xxx' paths if your file names are different!)
from app.model.user_project import UserProject 
from app.model.project import Project          
# ---------------------------------
import datetime

# ... (the rest of the code stays exactly the same)
from passlib.context import CryptContext # Standard password hasher for FastAPI/Python

# Setup the password hasher (adjust if you already have a hashing function in your app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_admin():
    db: Session = SessionLocal()
    try:
        # 1. Check if an admin already exists to prevent duplicates on restart
        existing_admin = db.query(User).filter(User.email == "admin@empdiary.com").first()
        
        if existing_admin:
            print("Default admin already exists. Skipping.")
            return

        # 2. Create the new admin user
        new_admin = User(
            name="System Admin",
            phone="0000000000",                  # Must be unique per your model
            email="maleeshadimal20@gmail.com",          # Must be unique per your model
            password=pwd_context.hash("Admin@123"), # CRITICAL: Hash the password!
            is_first_login=False,
            role="admin",                        # Override the default "intern" role
            created_at=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            is_active=True
        )
        
        # 3. Save to database
        db.add(new_admin)
        db.commit()
        print("✅ Default admin successfully created! You can now log in.")

    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_admin()