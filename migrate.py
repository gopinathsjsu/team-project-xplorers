from app.database import Base, engine
import app.models  # Ensure models are imported

print("Dropping old tables...")
Base.metadata.drop_all(engine)  # Deletes existing tables
print("Recreating tables...")
Base.metadata.create_all(engine)  # Creates new tables
print("Tables successfully created!")
