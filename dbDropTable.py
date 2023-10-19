from sqlalchemy import create_engine, MetaData, Table

# Create a database engine
engine = create_engine('sqlite:///window_activity.db')

# Create a metadata object
metadata = MetaData()

# Define the table you want to drop
your_table = Table('trailing_10_row_averages', metadata, autoload_with=engine)

# Drop the table
your_table.drop(engine)

# # Commit the changes (if applicable)
# engine.commit()

# # Close the database engine (if applicable)
# engine.close()
