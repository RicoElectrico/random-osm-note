import psycopg2
import json

# Connect to PostgreSQL
conn = psycopg2.connect(dbname="changesets")
cursor = conn.cursor()

# Read GeoJSON file
with open("osm-countries-0-001.geojson", "r") as geojson_file:
    geojson_data = json.load(geojson_file)

# Create a table with GeoJSON column
create_table_query = f"""
CREATE TABLE countries (
    iso_code text PRIMARY KEY,
    name text,
    geom geometry(Geometry, 4326)
);
"""
cursor.execute(create_table_query)
conn.commit()

# Insert GeoJSON features into the table
insert_query = f"""
INSERT INTO countries (iso_code, name, geom)
VALUES (%s, %s, ST_GeomFromGeoJSON(%s));
"""

for feature in geojson_data['features']:
    iso_code = feature['properties']['tags']['ISO3166-1']
    name = feature['properties']['tags']['name:en']
    geom = json.dumps(feature['geometry'])
    cursor.execute(insert_query, (iso_code, name, geom))

conn.commit()

# Close the connection
cursor.close()
conn.close()