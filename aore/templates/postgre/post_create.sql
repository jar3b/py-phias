CREATE INDEX "sphinx_ind_aolevel" ON "ADDROBJ" USING btree ("aolevel");
CREATE INDEX "sphinx_ind_parentguid" ON "ADDROBJ" USING btree ("parentguid");
CREATE INDEX "sphinx_ind_livestatus" ON "ADDROBJ" USING btree ("livestatus");
CREATE INDEX "sphinx_ind_aoguid" ON "ADDROBJ" USING btree ("aoguid");
CREATE INDEX "SOCRBASE_scname_idx" ON "SOCRBASE" USING btree ("scname");
CREATE INDEX "SOCRBASE_socrname_idx" ON "SOCRBASE" USING btree ("socrname");
CREATE INDEX "AOTRIG_word_idx" ON "AOTRIG" USING btree ("word");
