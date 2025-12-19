create table tt_tag_proportion as
select to_char(xx.creationdate, 'yyyy-mm-dd') as cdate , xx.id, xx.tag, xx.cnt, yy.tot_cnt, xx.cnt::FLOAT /yy.tot_cnt as pct
  from (
       select creationdate, id, tags, replace(replace(unnest(string_to_array(tags, '><')), '<', ''), '>', '') tag, 1 as cnt
        from public.posts
        where posttypeid = '1'
          and creationdate between '2021-11-30' and '2023-12-01'
          and tags like '%<python>%'

           ) xx,
       (
           select x.id, count(x.tag) as tot_cnt
              from (select creationdate, id, tags, replace(replace(unnest(string_to_array(tags, '><')), '<', ''), '>', '') tag
                      from public.posts
                    where posttypeid = '1'
                      and creationdate between '2021-11-30' and '2023-12-01'
                      and tags like '%<python>%') x
            group by x.id

           )yy
where xx.id = yy.id
;