

CREATE_ZONE_TABLE = '''CREATE TABLE zone
(
id       integer NOT NULL ,
name    timestamp NOT NULL ,
PRIMARY KEY (id)
);

CREATE INDEX zone_FK_1 ON zone (id);
SELECT AddGeometryColumn('zone', 'area', 4326, 'POLYGON', 'XY');'''
#   POLYGON((101.23 171.82, 201.32 101.5, 215.7 201.953, 101.23 171.82))
#   exterior ring, no interior rings
CREATE_ENTRY = 'INSERT INTO zone (drone_id,timestamp,area,picture_path,ai_predictions,csv_file_path) VALUES (? ,?,GeomFromText(?, 4326) ,? ,?,?);'
GET_ENTRYS_BY_TIMESTAMP = 'SELECT *, ST_AsText(area) AS geo FROM zone WHERE drone_id = ? AND timestamp > ? AND timestamp < ?;'
GET_ENTRY ='SELECT * FROM zone WHERE drone_id = ?;'