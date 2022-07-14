WITH RECURSIVE r AS (SELECT ao.parentguid, ao.shortname || ' ' || ao.formalname AS fullname
                     FROM "ADDROBJ" AS ao
                     WHERE aoid = $1
                     UNION
                     SELECT parent.parentguid,
                            parent.shortname || ' ' || parent.formalname || ', ' || r.fullname AS fullname
                     FROM "ADDROBJ" AS parent,
                          r
                     WHERE parent.aoguid = r.parentguid
                       AND actstatus = TRUE
                       AND livestatus = TRUE
                       AND nextid IS NULL)
SELECT fullname
FROM r
WHERE parentguid IS NULL LIMIT 1