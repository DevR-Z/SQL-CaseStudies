# <p align="center" style="margin-top: 0px;">Case Study #5: Data Mart
## <p align="center"><img src="https://github.com/DevR-Z/SQL-CaseStudies/blob/main/5%20-%20Data%20Mart/resources/c5.png?raw=true" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-5/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Data Mart is Danny’s latest venture and after running international operations for his online supermarket that specialises in fresh produce - Danny is asking for your support to analyse his sales performance.
In June 2020 - large scale supply changes were made at Data Mart. All Data Mart products now use sustainable packaging methods in every single step from the farm all the way to the customer.
Danny needs your help to quantify the impact of this change on the sales performance for Data Mart and it’s separate business areas.
The key business question he wants you to help him answer are the following:

	- What was the quantifiable impact of the changes introduced in June 2020?
	- Which platform, region, segment and customer types were the most impacted by this change?
	- What can we do about future introduction of similar sustainability updates to the business to minimise impact on sales?

## <p align="center">Questions
The following case study questions require some data cleaning steps before we start to unpack Danny’s key business questions in more depth.
### <p align="center">1. Data Cleansing Steps
#### In a single query, perform the following operations and generate a new table in the data_mart schema named clean_weekly_sales:

#### 1.Convert the week_date to a DATE format
```sql
alter table weekly_sales alter column week_date varchar(10);

with all_dates_cte as (
  select distinct week_date,
    charindex('/',week_date) first,right(week_date,len(week_date)-charindex('/',week_date)) week_date2,
    charindex('/',week_date)+charindex('/',right(week_date,len(week_date)-charindex('/',week_date))) second
  from weekly_sales
),new_dates as (
  select week_date,concat('20',right(week_date,len(week_date)-second),'-',
    case when len(substring(week_date,first+1,second-first-1))=1 then '0'+substring(week_date,first+1,second-first-1) else substring(week_date,first+1,second-first-1) end,'-',
    case when len(left(week_date,first-1))=1 then '0'+left(week_date,first-1) else left(week_date,first-1) end) new_week_date
  from all_dates_cte
)
update weekly_sales set week_date=n.new_week_date from weekly_sales t
inner join new_dates n on t.week_date=n.week_date;

alter table weekly_sales alter column week_date date

select table_name,column_name,data_type from information_schema.columns where table_name='weekly_sales' and column_name='week_date'
```
#### 2.Add a week_number as the second column for each week_date value, for example any value from the 1st of January to 7th of January will be 1, 8th to 14th will be 2 etc
```sql
alter table weekly_sales add week_number int;
update weekly_sales set week_number=datepart(week,week_date)
select top 10 * from weekly_sales;
```
#### 3.Add a month_number with the calendar month for each week_date value as the 3rd column
```sql
alter table weekly_sales add month_number int;
update weekly_sales set month_number=datepart(month,week_date);
select top 10 * from weekly_sales;
```
#### 4.Add a calendar_year column as the 4th column containing either 2018, 2019 or 2020 values
```sql
alter table weekly_sales add calendar_year int;
update weekly_sales set calendar_year=datepart(year,week_date);
select top 10 * from weekly_sales;
```
#### 5.Add a new column called age_band after the original segment column using the following mapping on the number inside the segment value

| segment | age_band      |
|---------|---------------|
| 1       | Young Adults  |
| 2       | Middle Aged   |
| 3 or 4  | Retirees      |

```sql
select distinct segment from weekly_sales;
update weekly_sales set segment=case when UPPER(segment)='NULL' then null else segment end;

alter table weekly_sales add age_band varchar(12);
update weekly_sales set age_band=case when segment is null then null
                                      when right(segment,1)='1' then 'Young Adults'
                                      when right(segment,1)='2' then 'Middle Aged'
                                      else 'Retirees' end;
select top 20 * from weekly_sales;
```
#### 6.Add a new demographic column using the following mapping for the first letter in the segment values:

| segment | demographic |
|---------|-------------|
| C       | Couples     |
| F       | Families    |

```sql
select distinct segment from weekly_sales;

alter table weekly_sales add demographic varchar(12);
update weekly_sales set demographic=case when left(segment,1)='C' then 'Couples'
                                        when left(segment,1)='F' then 'Families'
                                        else null end;
select top 20 * from weekly_sales;
```
#### 7.Ensure all null string values with an "unknown" string value in the original segment column as well as the new age_band and demographic columns
```sql
select * from information_schema.columns where table_name='weekly_sales' and column_name='segment'
alter table weekly_sales alter column segment varchar(7);
update weekly_sales set segment='unknown',
                        age_band='unknown',
                        demographic='unknown' 
where segment is null;
select top 20 * from weekly_sales
```
#### 8.Generate a new avg_transaction column as the sales value divided by transactions rounded to 2 decimal places for each record
```sql
alter table weekly_sales add avg_transaction decimal(8,2);
update weekly_sales set avg_transaction=round(sales*1.0/transactions,2);
select top 20 * from weekly_sales;
```
### <p align="center">2. Data Exploration
#### 1.What day of the week is used for each week_date value?
```sql
select distinct week_date,datepart(weekday,week_date) week_day,datename(weekday,week_date) week_date_name from weekly_sales
order by 1
```
#### 2.What range of week numbers are missing from the dataset?
```sql
with all_week_numbers as (
  select 1 as week_number
  union all
  select week_number+1 week_number from all_week_numbers
  where week_number<53
)
select * from all_week_numbers
where week_number not in (select distinct week_number from weekly_sales)
order by 1
```
#### 3.How many total transactions were there for each year in the dataset?
```sql
select calendar_year,count(*) nro_txn from weekly_sales
group by calendar_year
order by 1
```
#### 4.What is the total sales for each region for each month?
```sql
select distinct region from weekly_sales;

select column_name,data_type from information_schema.columns where table_name='weekly_sales' and column_name='sales'

select region,month_number,sum(cast(sales as bigint)) total_sales from weekly_sales
group by region,month_number
order by 1,3 desc;

select region,
  sum(coalesce(cast([1] as bigint),0)) 'Enero',sum(coalesce(cast([2] as bigint),0)) 'Febrero',
  sum(coalesce(cast([3] as bigint),0)) 'Marzo',sum(coalesce(cast([4] as bigint),0)) 'Abril',
  sum(coalesce(cast([5] as bigint),0)) 'Mayo',sum(coalesce(cast([6] as bigint),0)) 'Junio',
  sum(coalesce(cast([7] as bigint),0)) 'Julio',sum(coalesce(cast([8] as bigint),0)) 'Agosto',
  sum(coalesce(cast([9] as bigint),0)) 'Septiembre',sum(coalesce(cast([10] as bigint),0)) 'Octubre',
  sum(coalesce(cast([11] as bigint),0)) 'Noviembre',sum(coalesce(cast([12] as bigint),0)) 'Diciembre'
from weekly_sales
pivot(
  sum(sales)
  for month_number in ([1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12])
) as p
group by region
```
#### 5.What is the total count of transactions for each platform
```sql
select distinct platform from weekly_sales;
select platform,count(*) nro_txn from weekly_sales
group by platform
```
#### 6.What is the percentage of sales for Retail vs Shopify for each month?
```sql
select platform,month_number,round(count(*)*100.0/(select count(*) from weekly_sales),2) percentage from weekly_sales
group by platform,month_number
order by 1,2
```
#### 7.What is the percentage of sales by demographic for each year in the dataset?
```sql
select calendar_year,demographic,round(count(*)*100.0/(select count(*) from weekly_sales),2) percentage from weekly_sales
group by calendar_year,demographic
order by 1,3
```
#### 8.Which age_band and demographic values contribute the most to Retail sales?
```sql
select age_band,demographic,sum(cast(sales as bigint)) total_sales_retail from weekly_sales
where platform='Retail'
group by age_band,demographic
order by 3 desc
```
#### 9.Can we use the avg_transaction column to find the average transaction size for each year for Retail vs Shopify? If not - how would you calculate it instead?
```sql
select w1.platform,w1.calendar_year,
  round(sum(cast(sales as bigint))*100.0/(select sum(cast(w.sales as bigint)) from weekly_sales w where w1.platform=w.platform
                                    group by w.platform),2) percentage,
  round(sum(cast(sales as bigint))*1.0/sum(cast(transactions as bigint)),2) avg_txn_sales
from weekly_sales w1
group by w1.platform,w1.calendar_year
order by 1,2
```
### <p align="center">3. Before & After Analysis
This technique is usually used when we inspect an important event and want to inspect the impact before and after a certain point in time.
Taking the week_date value of 2020-06-15 as the baseline week where the Data Mart sustainable packaging changes came into effect.
We would include all week_date values for 2020-06-15 as the start of the period after the change and the previous week_date values would be before
Using this analysis approach - answer the following questions:
#### 1.What is the total sales for the 4 weeks before and after 2020-06-15? What is the growth or reduction rate in actual values and percentage of sales?
```sql
alter table weekly_sales alter column sales bigint;
select week_number,sum(sales) total_sales from weekly_sales 
where calendar_year=2020 and week_number between datepart(week,'2020-06-15')-4 and datepart(week,'2020-06-15')+4
group by week_number
order by 1
```
#### 2.What about the entire 12 weeks before and after?
```sql
select week_number,sum(sales) total_sales from weekly_sales 
where calendar_year=2020 and week_number between datepart(week,'2020-06-15')-12 and datepart(week,'2020-06-15')+12
group by week_number
order by 1
```
#### 3.How do the sale metrics for these 2 periods before and after compare with the previous years in 2018 and 2019?
```sql
with total_sales_2020 as (
  select week_number,
    sum(sales) total_sales,
    round(sum(sales)*100.0/(select sum(w.sales) from weekly_sales w where w.calendar_year=2020),3) percentage
  from weekly_sales 
  where calendar_year=2020 and week_number between datepart(week,'2020-06-15')-12 and datepart(week,'2020-06-15')+12 
  group by week_number
),total_sales_2019 as (
  select week_number,
    sum(sales) total_sales,
    round(sum(sales)*100.0/(select sum(w.sales) from weekly_sales w where w.calendar_year=2019),3) percentage
  from weekly_sales 
  where calendar_year=2019 and week_number between datepart(week,'2019-06-15')-12 and datepart(week,'2019-06-15')+12 
  group by week_number
),total_sales_2018 as (
  select week_number,
    sum(sales) total_sales,
    round(sum(sales)*100.0/(select sum(w.sales) from weekly_sales w where w.calendar_year=2018),3) percentage
  from weekly_sales 
  where calendar_year=2018 and week_number between datepart(week,'2018-06-15')-12 and datepart(week,'2018-06-15')+12 
  group by week_number
)
select t1.week_number,t1.total_sales t_2018,t1.percentage prtg_2018,
  t2.total_sales t_2019,t2.percentage prtg_2019,
  t3.total_sales t_2020,t3.percentage prtg_2020
from total_sales_2018 t1
inner join total_sales_2019 t2 on t1.week_number=t2.week_number
inner join total_sales_2020 t3 on t1.week_number=t3.week_number
order by 1
```
### <p align="center">4. Bonus Question
Which areas of the business have the highest negative impact in sales metrics performance in 2020 for the 12 week before and after period?
	- region
	- platform
	- age_band
	- demographic
	- customer_type
#### Do you have any further recommendations for Danny’s team at Data Mart or any interesting insights based off this analysis?
Analyzing region sales:
```sql
with region_sales as (
  select * from (
    select week_number,region,sales from weekly_sales
    where calendar_year=2020 and week_number between datepart(week,'2018-06-15')-12 and datepart(week,'2018-06-15')+12
  ) x
  pivot(
    sum(sales)
    for region in ([OCEANIA],[EUROPE],[SOUTH AMERICA],[AFRICA],[CANADA],[ASIA],[USA])
  ) AS p
)
select * from region_sales
union
select NULL,SUM([OCEANIA]),SUM([EUROPE]),SUM([SOUTH AMERICA]),SUM([AFRICA]),SUM([CANADA]),SUM([ASIA]),SUM([USA]) 
from region_sales
```
Analyzing platform sales:
```sql
with platform_sales as (
  select * from (
    select week_number,platform,sales from weekly_sales
    where calendar_year=2020 and week_number between datepart(week,'2018-06-15')-12 and datepart(week,'2018-06-15')+12
  ) x
  pivot(
    sum(sales)
    for platform in ([Retail],[Shopify])
  ) AS p
)
select * from platform_sales
union
select NULL,SUM([Retail]),SUM([Shopify]) 
from platform_sales
```