from app.database import Base, engine

# import all the models
# import app.models.UserModel, app.models.CustomerModel, app.models.AdminModel, app.models.RestaurantManagerModel
from app.models import UserModel, CustomerModel, AdminModel, RestaurantManagerModel

print("Dropping old tables...")
Base.metadata.drop_all(engine)  # Deletes existing tables
print("Recreating tables...")
Base.metadata.create_all(engine)  # Creates new tables
print("Tables successfully created!")
