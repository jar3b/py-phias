DROP TABLE IF EXISTS "public"."ADDROBJ";
CREATE TABLE "public"."ADDROBJ" (
  "id"         SERIAL4 NOT NULL,
  "aoid"       UUID    NOT NULL,
  "aoguid"     UUID,
  "shortname"  VARCHAR(10) COLLATE "default",
  "formalname" VARCHAR(120) COLLATE "default",
  "aolevel"    INT2,
  "parentguid" UUID,
  "actstatus"  BIT(1),
  "currstatus" INT2,
  PRIMARY KEY ("id", "aoid")
)
WITH (OIDS =FALSE
);
DROP TABLE IF EXISTS "public"."SOCRBASE";
CREATE TABLE "public"."SOCRBASE" (
  "id"       SERIAL4 NOT NULL,
  "level"    INT2,
  "scname"   VARCHAR(10),
  "socrname" VARCHAR(50),
  "kod_t_st" VARCHAR(4),
  PRIMARY KEY ("id")
)
WITH (OIDS =FALSE
);