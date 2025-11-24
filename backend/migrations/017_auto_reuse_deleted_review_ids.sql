CREATE OR REPLACE FUNCTION get_next_review_id()
RETURNS INTEGER AS $func$
DECLARE
    next_id INTEGER;
BEGIN
    SELECT COALESCE(MIN(t.id), 1)
    INTO next_id
    FROM (
        SELECT GENERATE_SERIES(1, (SELECT COALESCE(MAX(review_id), 0) FROM reviews) + 1) AS id
    ) t
    WHERE t.id NOT IN (SELECT review_id FROM reviews);
    
    RETURN next_id;
END;
$func$ LANGUAGE plpgsql;

DROP SEQUENCE IF EXISTS reviews_review_id_seq CASCADE;
CREATE SEQUENCE reviews_review_id_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE FUNCTION set_review_id_on_insert()
RETURNS TRIGGER AS $trig$
BEGIN
    IF NEW.review_id IS NULL THEN
        NEW.review_id := get_next_review_id();
    END IF;
    RETURN NEW;
END;
$trig$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_review_id_trigger ON reviews;

CREATE TRIGGER set_review_id_trigger
BEFORE INSERT ON reviews
FOR EACH ROW
EXECUTE FUNCTION set_review_id_on_insert();

ALTER TABLE reviews ALTER COLUMN review_id DROP DEFAULT;
