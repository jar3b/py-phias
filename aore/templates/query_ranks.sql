WITH data as (select *
              from json_to_recordset($1) as x("w" text, "bare" text)),
    d as (SELECT data.w, json_build_object('cnt_like', COUNT(t)) j FROM "AOTRIG" t RIGHT JOIN data ON word LIKE data.w || '%' GROUP BY w),
    d1 as (SELECT data.w, json_build_object('cnt_exact', COUNT(t)) j FROM "AOTRIG" t RIGHT JOIN data ON word = data.w  GROUP BY w),
    d2 as (SELECT data.w, json_build_object('cnt_socr', COUNT(s), 'scname', MAX(scname)) j FROM "SOCRBASE" s RIGHT JOIN data ON socrname ILIKE data.bare GROUP BY w),
    d3 as (SELECT data.w, json_build_object('cnt_socr_like', COUNT(s)) j FROM "SOCRBASE" s RIGHT JOIN data ON scname ILIKE data.bare GROUP BY w),
    d4 as (SELECT data.w, json_build_object('freq', max(frequency)) FROM "AOTRIG" t RIGHT JOIN data ON word = data.w GROUP BY w)
SELECT w, json_agg(j) FROM
                          (select * from d union all select * from d1 union all select * from d2 union all select * from d3 union all select * from d4) X group by w