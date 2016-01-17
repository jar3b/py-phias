
	WITH RECURSIVE PATH (cnt, aoid, aoguid, aolevel, fullname) AS (
	SELECT ao.id as cnt, ao.aoid, ao.aoguid, ao.aolevel,
	ao.shortname || ' ' || ao.formalname AS fullname
	FROM "ADDROBJ" AS ao
	WHERE aolevel = 1 AND actstatus = TRUE AND livestatus = TRUE AND nextid IS NULL
	UNION
	SELECT child.id as cnt, child.aoid, child.aoguid, child.aolevel,
	PATH.fullname || ', ' || child.shortname || ' ' || child.formalname AS fullname
	FROM "ADDROBJ" AS child
	, PATH
	WHERE child.parentguid = PATH.aoguid AND actstatus = TRUE AND livestatus = TRUE AND nextid IS NULL
	)
	SELECT * FROM PATH WHERE AOLEVEL NOT IN (1,3)