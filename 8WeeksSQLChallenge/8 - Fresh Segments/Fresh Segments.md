# <p align="center" style="margin-top: 0px;">Case Study #8: Fresh Segments
## <p align="center"><img src="https://github.com/DevR-Z/SQL-CaseStudies/blob/main/8WeeksSQLChallenge/8%20-%20Fresh%20Segments/resources/c8.png?raw=true" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-8/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Danny created Fresh Segments, a digital marketing agency that helps other businesses analyse trends in online ad click behaviour for their unique customer base.
Clients share their customer lists with the Fresh Segments team who then aggregate interest metrics and generate a single dataset worth of metrics for further analysis.
In particular - the composition and rankings for different interests are provided for each client showing the proportion of their customer list who interacted with online assets related to each interest for each month.
Danny has asked for your assistance to analyse aggregated metrics for an example client and provide some high level insights about the customer list and their interests.

## <p align="center">Questions
The following questions can be considered key business questions that are required to be answered for the Fresh Segments team.
Most questions can be answered using a single query however some questions are more open ended and require additional thought and not just a coded solution!

### <p align="center">A. Data Exploration and Cleansing
#### 1.Update the interest_metrics table by modifying the month_year column to be a date data type with the start of the month
```sql
alter table interest_metrics drop column month_year;
alter table interest_metrics add month_year date;
update interest_metrics set month_year=format(datefromparts(_year,_month,1),'yyyy-MM-dd');

select column_name,data_type from information_schema.columns where table_name='interest_metrics' and column_name='month_year';
```
#### 2.What is count of records in the interest_metrics for each month_year value sorted in chronological order (earliest to latest) with the null values appearing first?
```sql
select month_year,count(interest_id) nro_records from interest_metrics
group by month_year
order by 1
```
--3.What do you think we should do with these null values in the interest_metrics


#### 4.How many interest_id values exist in the interest_metrics table but not in the interest_map table? What about the other way around?
```sql
alter table interest_metrics alter column interest_id int;

select count(distinct interest_id) not_in_map from interest_metrics
where interest_id not in (select distinct id from interest_map);

select count(distinct map.id) not_in_metrics from interest_metrics mtrc
right join interest_map map on mtrc.interest_id=map.id
where mtrc.interest_id is null;
```
#### 5.Summarise the id values in the interest_map by its total record count in this table
```sql
select id,count(id) nro_records from interest_map
group by id
order by 2 desc

select interest_id,count(*) nro_records from interest_metrics
group by interest_id
order by 2 desc
```
#### 6.What sort of table join should we perform for our analysis and why? Check your logic by checking the rows where interest_id = 21246 in your joined output and include all columns from interest_metrics and all columns from interest_map except from the id column.
```sql
select * from interest_metrics mtr
inner join interest_map m on mtr.interest_id=m.id
where mtr.interest_id=21246 and mtr._month is not null
```
#### 7.Are there any records in your joined table where the month_year value is before the created_at value from the interest_map table? Do you think these values are valid and why?
```sql
select mtr.interest_id,mtr.month_year,m.created_at,m.last_modified from interest_metrics mtr
inner join interest_map m on mtr.interest_id=m.id
where mtr._month is not null and mtr.month_year<m.created_at --Se pidio que se pusiera el primer dia de cada mes en month_year, por eso existe este tipo de casos

select mtr.interest_id,mtr.month_year,m.created_at,m.last_modified from interest_metrics mtr
inner join interest_map m on mtr.interest_id=m.id
where mtr._month is not null and month(mtr.month_year)<month(m.created_at) and year(mtr.month_year)<year(m.created_at)
```
### <p align="center">B. Interest Analysis
#### 1.Which interests have been present in all month_year dates in our dataset?
```sql
with cte as (
  select interest_id,count(distinct month_year) nro_months_in_dataset from interest_metrics
  group by interest_id
  having count(distinct month_year)=(select count(distinct month_year) from interest_metrics)
)
select nro_months_in_dataset,count(interest_id) total_interest_in_all_months from cte
group by nro_months_in_dataset
```
#### 2.Using this same total_months measure - calculate the cumulative percentage of all records starting at 14 months - which total_months value passes the 90% cumulative percentage value?
```sql
with total_months as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
),total_interest_by_total_months as (
  select nro_months_appears total_month,count(interest_id) nro_interest from total_months
  group by nro_months_appears
),percentage_cte as (
  select total_month,nro_interest,
    round(sum(nro_interest) over(order by total_month desc)*100.0/(select sum(nro_interest) from total_interest_by_total_months),2) percentage_flag
  from total_interest_by_total_months
)
select top 1 * from percentage_cte where percentage_flag>90.0

with cte as (
  select month_year,count(interest_id) nro_records from interest_metrics
  where month_year is not null
  group by month_year
),acumulative_percentage as (
  select *,
    round((sum(nro_records) over(order by month_year))*100.0/(select sum(nro_records) from cte),2) percentage 
  from cte
)
select * from acumulative_percentage where percentage>90
```
#### 3.If we were to remove all interest_id values which are lower than the total_months value we found in the previous question - how many total data points would we be removing?
```sql
with total_months_flag as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
)
select count(*) nro_data_to_remove from interest_metrics
where interest_id in (select interest_id from total_months_flag)
```
#### 4.Does this decision make sense to remove these data points from a business perspective? Use an example where there are all 14 months present to a removed interest example for your arguments - think about what it means to have less months present from a segment perspective.

#### 5.After removing these interests - how many unique interests are there for each month?
```sql
with interest_to_remove as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
)
select month_year,count(distinct interest_id) nro_interest_after_remove from interest_metrics
where interest_id not in (select interest_id from total_months_flag) and month_year is not null
group by month_year
order by 1
```
### <p align="center">C. Segment Analysis
#### 1.Using our filtered dataset by removing the interests with less than 6 months worth of data, which are the top 10 and bottom 10 interests which have the largest composition values in any month_year? Only use the maximum composition value for each interest but you must keep the corresponding month_year
```sql
with interest_to_remove as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
),top_10 as (
  select month_year,interest_id,
    max(composition) max_composition_by_month,dense_rank() over(order by max(composition) desc) d_rnk
    from interest_metrics
  where interest_id not in (select interest_id from interest_to_remove) and month_year is not null
  group by month_year,interest_id
),bottom_10 as (
  select month_year,interest_id,
  max(composition) max_composition_by_month,dense_rank() over(order by max(composition)) d_rnk
  from interest_metrics
  where interest_id not in (select interest_id from interest_to_remove) and month_year is not null
  group by month_year,interest_id
)
select month_year,interest_id,max_composition_by_month,'top_10' flag from top_10 where d_rnk<=10
union
select month_year,interest_id,max_composition_by_month,'bottom_10' flag from bottom_10 where d_rnk<=10
```
#### 2.Which 5 interests had the lowest average ranking value?
```sql
with interest_to_remove as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
)
select top 5 interest_id,avg(ranking) avg_ranking from interest_metrics
where month_year is not null and interest_id not in (select interest_id from interest_to_remove)
group by interest_id
order by 2
```
#### 3.Which 5 interests had the largest standard deviation in their percentile_ranking value?
```sql
with interest_to_remove as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
)
select top 5 interest_id,round(stdev(percentile_ranking),2) desv_est_percentile_ranking from interest_metrics
where month_year is not null and interest_id not in (select interest_id from interest_to_remove)
group by interest_id
order by 2 desc
```
#### 4.For the 5 interests found in the previous question - what was minimum and maximum percentile_ranking values for each interest and its corresponding year_month value? Can you describe what is happening for these 5 interests?
```sql
with interest_to_remove as (
  select interest_id,count(distinct month_year) nro_months_appears from interest_metrics
  where month_year is not null
  group by interest_id
  having count(distinct month_year)<=6
),top_5 as (
  select interest_id,round(stdev(percentile_ranking),2) desv_est_percentile_ranking,
    dense_rank() over(order by round(stdev(percentile_ranking),2) desc) d_rnk
  from interest_metrics
  where month_year is not null and interest_id not in (select interest_id from interest_to_remove)
  group by interest_id
),min_max_percentile as (
  select m.interest_id,min(m.percentile_ranking) min_percentile,max(m.percentile_ranking) max_percentile from interest_metrics m
  inner join top_5 t on m.interest_id=t.interest_id
  where t.d_rnk<=5
  group by m.interest_id
)
select mm.interest_id,m1.month_year min_percentile_month_year,mm.min_percentile,
  m2.month_year max_percentile_month_year,mm.max_percentile 
from min_max_percentile mm
inner join interest_metrics m1 on mm.interest_id=m1.interest_id and mm.min_percentile=m1.percentile_ranking
inner join interest_metrics m2 on mm.interest_id=m2.interest_id and mm.max_percentile=m2.percentile_ranking
```
#### 5.How would you describe our customers in this segment based off their composition and ranking values? What sort of products or services should we show to these customers and what should we avoid?

### <p align="center">D. Index Analysis
The index_value is a measure which can be used to reverse calculate the average composition for Fresh Segments’ clients.
Average composition can be calculated by dividing the composition column by the index_value column rounded to 2 decimal places.
#### 1.What is the top 10 interests by the average composition for each month?
```sql
with avg_composition_by_month as (
  select month_year,interest_id,round(composition/index_value,2) avg_composition,
    dense_rank() over(partition by month_year order by round(composition/index_value,2) desc) d_rnk
  from interest_metrics
  where month_year is not null
)
select * from avg_composition_by_month where d_rnk<=10
```
#### 2.For all of these top 10 interests - which interest appears the most often?
```sql
with avg_composition_by_month as (
  select month_year,interest_id,round(composition/index_value,2) avg_composition,
    dense_rank() over(partition by month_year order by round(composition/index_value,2) desc) d_rnk
  from interest_metrics
  where month_year is not null
)
select interest_id,count(interest_id) count_interest from avg_composition_by_month where d_rnk<=10
group by interest_id
order by 2 desc
```
#### 3.What is the average of the average composition for the top 10 interests for each month?
```sql
with avg_avg_composition_by_month as (
  select month_year,interest_id,avg(round(composition/index_value,2)) avg_composition,
    dense_rank() over(partition by month_year order by avg(round(composition/index_value,2)) desc) d_rnk
  from interest_metrics
  where month_year is not null
  group by month_year,interest_id
)
select * from avg_avg_composition_by_month where d_rnk<=10
```
#### 4.What is the 3 month rolling average of the max average composition value from September 2018 to August 2019 and include the previous top ranking interests in the same output shown below.
```sql
with cte as (
  select month_year,interest_id,round(composition/index_value,2) avg_composition,
    round(max(composition/index_value) over(partition by month_year order by month_year),2) max_avg_composition 
  from interest_metrics
),max_avg_composition_cte as (
  select * from cte
  where avg_composition=max_avg_composition
),month_moving_cte as (
  select m.month_year,i.interest_name,m.max_avg_composition,
    round(avg(m.max_avg_composition) over(order by m.month_year rows between 2 preceding and current row),2) '3_month_moving_avg',
    lag(i.interest_name) over(order by m.month_year)+':'+cast(lag(m.max_avg_composition) over(order by m.month_year) as varchar) '1_month_ago',
    lag(i.interest_name,2) over(order by m.month_year)+':'+cast(lag(m.max_avg_composition,2) over(order by m.month_year) as varchar) '2_month_ago'
  from max_avg_composition_cte m
  inner join interest_map i on m.interest_id=i.id
)
select * from month_moving_cte
where month_year between '2018-09-01' and '2019-08-31'
```
#### 5.Provide a possible reason why the max average composition might change from month to month? Could it signal something is not quite right with the overall business model for Fresh Segments?