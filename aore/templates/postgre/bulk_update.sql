DROP TABLE IF EXISTS "%tablename%_TEMP";
CREATE TEMP TABLE "%tablename%_TEMP" ON COMMIT DROP AS SELECT *
                                                       FROM "%tablename%" WITH NO DATA;
COPY "%tablename%_TEMP" (%fieldslist%) FROM '%csvname%' DELIMITER '%tab%' NULL 'NULL';
INSERT INTO "%tablename%" (%fieldslist%) SELECT %fieldslist%
FROM
"%tablename%_TEMP" ON CONFLICT (%uniquekey%) DO UPDATE SET %updaterule%;