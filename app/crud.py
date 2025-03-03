from sqlalchemy.orm import Session
from app.models import UserModel, CustomerModel, AdminModel, RestaurantManagerModel
from passlib.context import CryptContext
from app.schemas import UserSchema
from app.models.UserModel import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()

def create_user(db: Session, user: UserSchema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel.User(
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Create an entry in the respective table based on the user's role
    if user.role.name == UserRole.CUSTOMER.name:
        db_customer = CustomerModel.Customer(
            user_id=db_user.user_id,
            notification_preference=CustomerModel.NotificationPreference.EMAIL  # Default value
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
    elif user.role.name == UserRole.ADMIN.name:
        db_admin = AdminModel.Admin(
            user_id=db_user.user_id
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
    elif user.role.name == UserRole.RESTAURANT_MANAGER.name:
        db_manager = RestaurantManagerModel.RestaurantManager(
            user_id=db_user.user_id,
            approved_at=None  # Default value, can be updated later
        )
        db.add(db_manager)
        db.commit()
        db.refresh(db_manager)

    return db_user

def get_user(db: Session, user_id: int):
    return db.query(UserModel.User).filter(UserModel.User.user_id == user_id).first()