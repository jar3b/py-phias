WITH RECURSIVE child_to_parents AS (SELECT "ADDROBJ".*
                                    FROM "ADDROBJ"
                                    WHERE aoid = $1
                                    UNION ALL
                                    SELECT "ADDROBJ".*
                                    FROM "ADDROBJ",
                                         child_to_parents
                                    WHERE "ADDROBJ".aoguid = child_to_parents.parentguid
                                      AND "ADDROBJ".actstatus = True
                                      AND "ADDROBJ".livestatus = True
                                      AND "ADDROBJ".nextid IS NULL)
SELECT cs.aoid, cs.aoguid, cs.shortname, cs.formalname, cs.aolevel, cs.regioncode, s.socrname
FROM child_to_parents cs
         LEFT OUTER JOIN "SOCRBASE" s
                         ON s.scname = cs.shortname AND s.level = cs.aolevel
ORDER BY aolevel;
