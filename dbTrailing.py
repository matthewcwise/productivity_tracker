from sqlalchemy import create_engine, text  # Import 'text' function

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the SQL query to create the table
create_table_query = """
CREATE TABLE trailing_10_row_averages_table AS
SELECT 
    le.timestamp, 
    wc.window_category,
    AVG(le2.keyboard_events) AS keyboard_count,
    AVG(le2.mouse_events) AS click_count
FROM
    log_entries le

LEFT JOIN
    log_entries le2 ON le.id - le2.id BETWEEN 0 AND 9

LEFT JOIN
    window_categories wc
ON
    le.window_title = wc.window_title
    AND le.window_url_base = wc.window_url_base

GROUP BY
    le.timestamp, wc.window_category;
"""

# Execute the SQL query to create the table
with engine.connect() as connection:
    connection.execute(text(create_table_query))
