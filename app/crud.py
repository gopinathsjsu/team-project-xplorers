from sqlalchemy.orm import Session
from app.models import UserModel, CustomerModel, AdminModel, RestaurantManagerModel, RestaurantModel
from passlib.context import CryptContext
from app.schemas import UserSchema, RestaurantSchema
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

def create_restaurant(db: Session, restaurant: RestaurantSchema.RestaurantCreate, manager_id: int):
    db_restaurant = RestaurantModel.Restaurant(
        manager_id=manager_id,
        name=restaurant.name,
        description=restaurant.description,
        address_line1=restaurant.address_line1,
        address_line2=restaurant.address_line2,
        city=restaurant.city,
        state=restaurant.state,
        zip_code=restaurant.zip_code,
        phone_number=restaurant.phone_number,
        email=restaurant.email,
        cuisine_type=restaurant.cuisine_type,
        cost_rating=restaurant.cost_rating
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def get_all_restaurants(db: Session):
    return db.query(RestaurantModel.Restaurant).all()

def get_restaurants_by_manager(db: Session, manager_id: int):
    return db.query(RestaurantModel.Restaurant).filter(RestaurantModel.Restaurant.manager_id == manager_id).all()