
	WITH RECURSIVE PATH (cnt, aoid, aoguid, aolevel, fullname) AS (
	SELECT ao.id as cnt, ao.aoid, ao.aoguid, ao.aolevel,
	ao.shortname || ' ' || ao.formalname AS fullname
	FROM "ADDROBJ" AS ao
	WHERE aolevel = 1 AND livestatus = TRUE
	UNION
	SELECT child.id as cnt, child.aoid, child.aoguid, child.aolevel,
	PATH.fullname || ', ' || child.shortname || ' ' || child.formalname AS fullname
	FROM "ADDROBJ" AS child
	, PATH
	WHERE child.parentguid = PATH.aoguid AND livestatus = TRUE
	)
	SELECT * FROM PATH WHERE AOLEVEL NOT IN (1,3)