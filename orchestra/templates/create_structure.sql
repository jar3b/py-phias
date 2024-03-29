CREATE EXTENSION IF NOT EXISTS pg_trgm;
DROP TABLE IF EXISTS "ADDROBJ";
CREATE TABLE "ADDROBJ"
(
    "id"         SERIAL4 NOT NULL,
    "aoid"       UUID    NOT NULL,
    "aoguid"     UUID,
    "shortname"  VARCHAR(10) COLLATE "default",
    "formalname" VARCHAR(120) COLLATE "default",
    "aolevel"    INT2,
    "parentguid" UUID,
    "actstatus"  BOOL,
    "livestatus" BOOL,
    "nextid"     UUID,
    "regioncode" int2,
    CONSTRAINT "aoid" UNIQUE ("aoid"),
    CONSTRAINT "id_addrobj" PRIMARY KEY ("id")
) WITH (OIDS = FALSE);
DROP TABLE IF EXISTS "SOCRBASE";
CREATE TABLE "SOCRBASE"
(
    "id"       SERIAL4 NOT NULL,
    "level"    INT2,
    "scname"   VARCHAR(10),
    "socrname" VARCHAR(50),
    "kod_t_st" VARCHAR(4),
    CONSTRAINT "kod_t_st" UNIQUE ("kod_t_st"),
    CONSTRAINT "id_socrbase" PRIMARY KEY ("id")
) WITH (OIDS = FALSE);
DROP TABLE IF EXISTS "AOTRIG";
CREATE TABLE "AOTRIG"
(
    "id"        SERIAL4 NOT NULL,
    "word"      VARCHAR(50),
    "trigramm"  VARCHAR(180),
    "frequency" INT4,
    CONSTRAINT "word" UNIQUE ("word"),
    CONSTRAINT "id_aotrig" PRIMARY KEY ("id")
) WITH (OIDS = FALSE);