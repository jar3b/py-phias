% for table_name in table_names:
%   if table_name == "ADDROBJ":
DROP INDEX IF EXISTS "sphinx_ind_aolevel";
DROP INDEX IF EXISTS "sphinx_ind_parentguid";
DROP INDEX IF EXISTS "sphinx_ind_livestatus";
DROP INDEX IF EXISTS "sphinx_ind_aoguid";
%   end
%   if table_name == "SOCRBASE":
DROP INDEX IF EXISTS "SOCRBASE_scname_idx";
DROP INDEX IF EXISTS "SOCRBASE_socrname_idx";
DROP INDEX IF EXISTS "SOCRBASE_scname_gin_idx";
DROP INDEX IF EXISTS "SOCRBASE_socrname_gin_idx";
%   end
%   if table_name == "AOTRIG":
DROP INDEX IF EXISTS "AOTRIG_word_idx";
DROP INDEX IF EXISTS "AOTRIG_word_gin_idx";
%   end
% end
