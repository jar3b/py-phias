DROP TABLE IF EXISTS "{{tablename}}_TEMP";
CREATE TEMP TABLE "{{tablename}}_TEMP" ON COMMIT DROP AS SELECT *
                                                       FROM "{{tablename}}" WITH NO DATA;
COPY "{{tablename}}_TEMP" ({{fieldslist}}) FROM '{{csvname}}' DELIMITER '{{delim}}' NULL 'NULL';
DELETE FROM "{{tablename}}" WHERE {{uniquekey}} IN (SELECT {{uniquekey}} FROM "{{tablename}}_TEMP");