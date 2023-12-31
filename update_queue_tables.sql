DELETE FROM note_queue
WHERE id IN (
    SELECT id
    FROM note
    WHERE closed_at IS NOT NULL
);
DELETE FROM note_country_queue
WHERE id IN (
    SELECT id
    FROM note
    WHERE closed_at IS NOT NULL
);
-- Common Table Expression (CTE) to get the IDs of open notes to be inserted into note_queue
WITH min_global_seq_number AS (
    SELECT min(seq_number) AS seq_number FROM note_queue),
    min_country_seq_number AS (
    SELECT country_code, min(seq_number) AS seq_number FROM note_country_queue GROUP BY country_code
    ),
    open_notes_to_insert AS (
    INSERT INTO note_queue (id, seq_number, lat, lon)
    SELECT
        n.id,
        (SELECT seq_number from min_global_seq_number),
        n.lat,
        n.lon
    FROM
        note n
    WHERE
        n.closed_at IS NULL
        AND NOT EXISTS (
            SELECT 1
            FROM note_queue
            WHERE id = n.id
        )
    RETURNING id
)
-- Insert open notes into note_country_queue that are not already present
INSERT INTO note_country_queue (id, country_code, seq_number, lat, lon)
SELECT
    n.id,
    c.iso_code AS country_code,
    (SELECT seq_number from min_country_seq_number m WHERE c.iso_code = m.country_code),
    n.lat,
    n.lon
FROM
    note n
JOIN
    countries c ON ST_Intersects(n.geom, c.geom)
WHERE
    n.closed_at IS NULL
    AND n.id IN (SELECT id FROM open_notes_to_insert);