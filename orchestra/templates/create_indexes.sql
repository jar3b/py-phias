-- ADDROBJ
CREATE INDEX "sphinx_ind_aolevel" ON "ADDROBJ" USING btree ("aolevel");
CREATE INDEX "sphinx_ind_parentguid" ON "ADDROBJ" USING btree ("parentguid");
CREATE INDEX "sphinx_ind_livestatus" ON "ADDROBJ" USING btree ("actstatus", "livestatus", "nextid");
CREATE INDEX "sphinx_ind_aoguid" ON "ADDROBJ" USING btree ("aoguid");
-- SOCRBASE
CREATE INDEX "SOCRBASE_scname_idx" ON "SOCRBASE" USING btree ("scname");
CREATE INDEX "SOCRBASE_socrname_idx" ON "SOCRBASE" USING btree ("socrname");
CREATE INDEX "SOCRBASE_scname_gin_idx" ON "SOCRBASE" USING gin(scname gin_trgm_ops);
CREATE INDEX "SOCRBASE_socrname_gin_idx" ON "SOCRBASE" USING gin(socrname gin_trgm_ops);
create unique index "SOCRBASE_uniq_idx" on "SOCRBASE" (level, scname);
-- AOTRIG
CREATE INDEX "AOTRIG_word_idx" ON "AOTRIG" USING btree ("word");
CREATE INDEX "AOTRIG_word_gin_idx" ON "AOTRIG" USING gin(word gin_trgm_ops);
