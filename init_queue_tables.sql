CREATE TABLE note_queue (
    id bigint,
    seq_number bigint DEFAULT 0,
    rand real DEFAULT random(),
    lat real,
    lon real
);

INSERT INTO note_queue (id, lat, lon)
SELECT
    n.id,
    n.lat,
    n.lon
FROM
    note n
WHERE
    n.closed_at IS NULL;

CREATE TABLE note_country_queue (
    id bigint,
    country_code text,
    seq_number bigint DEFAULT 0,
    rand real DEFAULT random(),
    lat real,
    lon real
);

INSERT INTO note_country_queue (id, country_code, lat, lon)
SELECT
    n.id,
    c.iso_code AS country_code,
    n.lat,
    n.lon
FROM
    note n
JOIN
    countries c ON ST_Intersects(n.geom, c.geom)
WHERE
    n.closed_at IS NULL;

CREATE INDEX idx_note_queue ON note_queue (seq_number, rand);
CREATE INDEX idx_note_queue_id ON note_queue (id);

CREATE INDEX idx_note_country_queue ON note_country_queue (country_code, seq_number, rand);
CREATE INDEX idx_note_country_queue_id ON note_country_queue (id);
GRANT ALL ON note_queue TO "www-data" ;
GRANT ALL ON note_country_queue TO "www-data" ;