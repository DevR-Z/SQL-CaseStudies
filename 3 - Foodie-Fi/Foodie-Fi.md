# <p align="center" style="margin-top: 0px;">Case Study #3: Foodie-Fi 
## <p align="center"><img src="https://github.com/DevR-Z/SQL-CaseStudies/blob/main/3%20-%20Foodie-Fi/resources/c3.png?raw=true" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-3/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Subscription based businesses are super popular and Danny realised that there was a large gap in the market - he wanted to create a new streaming service that only had food related content - something like Netflix but with only cooking shows!

Danny finds a few smart friends to launch his new startup Foodie-Fi in 2020 and started selling monthly and annual subscriptions, giving their customers unlimited on-demand access to exclusive food videos from around the world!

Danny created Foodie-Fi with a data driven mindset and wanted to ensure all future investment decisions and new features were decided using data. This case study focuses on using subscription style digital data to answer important business questions.

## <p align="center">Questions
This case study is split into an initial data understanding question before diving straight into data analysis questions before finishing with 1 single extension challenge.

### <p align="center">A. Customer Journey
#### 1.Based off the 8 sample customers provided in the sample from the subscriptions table, write a brief description about each customer’s onboarding journey.
```sql
select top 10 s.customer_id,s.plan_id,p.plan_name,p.price from subscriptions s
inner join plans p on s.plan_id=p.plan_id
order by customer_id
```
Each customer can try "trial" plan that is free and they can join to any plan (basic,pro,etc) with their respective amount

### <p align="center">B. Data Analysis Questions
#### 1.How many customers has Foodie-Fi ever had?
```sql
select count(distinct customer_id) nro_customers from subscriptions
```
#### 2.What is the monthly distribution of trial plan start_date values for our dataset - use the start of the month as the group by value
```sql
select format(datefromparts(year(start_date),month(start_date),1),'dd-MM-yyyy') date_format,count(customer_id) nro_trials from subscriptions
where plan_id=0
group by format(datefromparts(year(start_date),month(start_date),1),'dd-MM-yyyy')
order by 1
```
#### 3.What plan start_date values occur after the year 2020 for our dataset? Show the breakdown by count of events for each plan_name
```sql
with cte as (
  select p.plan_id,coalesce(count(s.customer_id),0) nro_customers_aft_2020 from plans p
  left join subscriptions s on p.plan_id=s.plan_id
  where year(s.start_date)>2020
  group by p.plan_id,p.plan_name
)
select p.plan_id,p.plan_name,coalesce(cte.nro_customers_aft_2020,0) nro_customers_aft_2020 from cte
right join plans p on cte.plan_id=p.plan_id
```
#### 4.What is the customer count and percentage of customers who have churned rounded to 1 decimal place?
```sql
select count(distinct customer_id) nro_churned,
  round(count(distinct customer_id)*100.0/(select count(distinct customer_id) from subscriptions),1) percentage_churned 
from subscriptions
where plan_id=4
```
#### 5.How many customers have churned straight after their initial free trial - what percentage is this rounded to the nearest whole number?
```sql
with cte as (
  select customer_id,plan_id,lag(plan_id) over(partition by customer_id order by start_date) prev_plan from subscriptions
)
select count(customer_id) nro_cust_churned_aft_trial,
  round(count(customer_id)*100.0/(select count(distinct customer_id) from subscriptions),1) percentage_churned_aft_trial
from cte
where plan_id=4 and prev_plan=0
```
#### 6.What is the number and percentage of customer plans after their initial free trial?
```sql
with cte as (
  select customer_id,plan_id,lag(plan_id) over(partition by customer_id order by start_date) prev_plan from subscriptions
)
select plan_id,count(distinct customer_id) nro_customers_after_trial from cte
where prev_plan=0
group by plan_id
```
#### 7.What is the customer count and percentage breakdown of all 5 plan_name values at 2020-12-31?
```sql
with cte as (
  select customer_id,plan_id from subscriptions
  where year(start_date)<2021
)
select p.plan_id,p.plan_name,count(distinct cte.customer_id) nro_cust_bef_2021,
  round(count(distinct cte.customer_id)*100.0/(select count(distinct customer_id) from subscriptions),1) percentage_cust_bef_2021
from cte
inner join plans p on cte.plan_id=p.plan_id
group by p.plan_id,p.plan_name
order by 1
```
#### 8.How many customers have upgraded to an annual plan in 2020?
```sql
select plan_id,count(distinct customer_id) nro_customers from subscriptions
where year(start_date)<2021 and plan_id=3
group by plan_id
```
#### 9.How many days on average does it take for a customer to an annual plan from the day they join Foodie-Fi?
```sql
with cte as (
  select s.customer_id,min(s.start_date) join_date,
    (select start_date from subscriptions s1 where plan_id=3 and s1.customer_id=s.customer_id) anual_plan_start_date
  from subscriptions s
  group by s.customer_id
)
select avg(datediff(day,join_date,anual_plan_start_date)) avg_days_become_anual from cte
where anual_plan_start_date is not null
```
#### 10.Can you further breakdown this average value into 30 day periods (i.e. 0-30 days, 31-60 days etc)
```sql
with cte as (
  select s.customer_id,min(s.start_date) join_date,
    (select start_date from subscriptions s1 where plan_id=3 and s1.customer_id=s.customer_id) anual_plan_start_date
  from subscriptions s
  group by s.customer_id
),days_became_anual_cte as (
  select *,datediff(day,join_date,anual_plan_start_date) days_became_anual from cte
  where anual_plan_start_date is not null
)
select '0-30 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=0 and days_became_anual<=30
union
select '31-60 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=31 and days_became_anual<=60
union
select '61-90 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=61 and days_became_anual<=90
union
select '91-120 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=91 and days_became_anual<=120
union
select '121-150 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=121 and days_became_anual<=150
union
select '151-180 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=151 and days_became_anual<=180
union
select '181-210 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=181 and days_became_anual<=210
union
select '211-240 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=211 and days_became_anual<=240
union
select '241-270 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=241 and days_became_anual<=270
union
select '271-300 days' periods,round(avg(days_became_anual*1.0),2) avg_days_become_anual 
from days_became_anual_cte where days_became_anual>=271 and days_became_anual<=300
```
#### 11.How many customers downgraded from a pro monthly to a basic monthly plan in 2020?
```sql
with cte as (
  select customer_id,plan_id,start_date,
  lag(plan_id) over(partition by customer_id order by start_date) prev_plan from subscriptions
)
select count(distinct customer_id) nro_cust_downg from cte
where year(start_date)<2021 and plan_id=2 and prev_plan=1
```

### <p align="center">C. Challenge Payment Question
#### 1.The Foodie-Fi team wants you to create a new payments table for the year 2020 that includes amounts paid by each customer in the subscriptions table with the following requirements:

	- monthly payments always occur on the same day of month as the original start_date of any monthly paid plan
	- upgrades from basic to monthly or pro plans are reduced by the current paid amount in that month and start immediately
	- upgrades from pro monthly to pro annual are paid at the end of the current billing period and also starts at the end of the month period
	-once a customer churns they will no longer make payments*/
Example outputs for this table might look like the following:

| customer_id | plan_id | plan_name      | payment_date | amount | payment_order |
|-------------|---------|----------------|--------------|--------|---------------|
| 1           | 1       | basic monthly  | 2020-08-08   | 9.90   | 1             |
| 1           | 1       | basic monthly  | 2020-09-08   | 9.90   | 2             |
| 1           | 1       | basic monthly  | 2020-10-08   | 9.90   | 3             |
| 1           | 1       | basic monthly  | 2020-11-08   | 9.90   | 4             |
| 1           | 1       | basic monthly  | 2020-12-08   | 9.90   | 5             |
| 2           | 3       | pro annual     | 2020-09-27   | 199.00 | 1             |
| 13          | 1       | basic monthly  | 2020-12-22   | 9.90   | 1             |
| 15          | 2       | pro monthly    | 2020-03-24   | 19.90  | 1             |
| 15          | 2       | pro monthly    | 2020-04-24   | 19.90  | 2             |
| 16          | 1       | basic monthly  | 2020-06-07   | 9.90   | 1             |
| 16          | 1       | basic monthly  | 2020-07-07   | 9.90   | 2             |
| 16          | 1       | basic monthly  | 2020-08-07   | 9.90   | 3             |
| 16          | 1       | basic monthly  | 2020-09-07   | 9.90   | 4             |
| 16          | 1       | basic monthly  | 2020-10-07   | 9.90   | 5             |
| 16          | 3       | pro annual     | 2020-10-21   | 189.10 | 6             |
| 18          | 2       | pro monthly    | 2020-07-13   | 19.90  | 1             |
| 18          | 2       | pro monthly    | 2020-08-13   | 19.90  | 2             |
| 18          | 2       | pro monthly    | 2020-09-13   | 19.90  | 3             |
| 18          | 2       | pro monthly    | 2020-10-13   | 19.90  | 4             |
| 18          | 2       | pro monthly    | 2020-11-13   | 19.90  | 5             |
| 18          | 2       | pro monthly    | 2020-12-13   | 19.90  | 6             |
| 19          | 2       | pro monthly    | 2020-06-29   | 19.90  | 1             |
| 19          | 2       | pro monthly    | 2020-07-29   | 19.90  | 2             |
| 19          | 3       | pro annual     | 2020-08-29   | 199.00 | 3             |

```sql
with cte as (
  select customer_id,plan_id,start_date payment_date,
    (select start_date from subscriptions s1 where s.customer_id=s1.customer_id and plan_id=4 and year(s1.start_date)<2021) churn_date from subscriptions s
  where customer_id in (1,2,13,15,16,18,19) and plan_id in (1,2)
  union all
  select customer_id,plan_id,dateadd(month,1,payment_date) payment_date,churn_date from cte
  where month(payment_date)<12
),start_date_plan_cte as (
  select customer_id,plan_id,min(payment_date) start_plan from cte
  group by customer_id,plan_id
),part_plans_cte as (
  select * from cte 
  where (datediff(day,payment_date,churn_date)>0 or churn_date is null) and
      EXISTS(select start_plan from start_date_plan_cte s where cte.customer_id=s.customer_id and cte.payment_date<=s.start_plan)
),churned_plans_cte as (
  select customer_id,plan_id,max(payment_date) start_plan,churn_date from part_plans_cte
  where churn_date is not null
  group by customer_id,plan_id,churn_date
  union all
  select customer_id,plan_id,dateadd(month,1,start_plan) start_plan,churn_date from churned_plans_cte
  where dateadd(month,1,start_plan)<churn_date
),all_plans_cte as (
  select customer_id,max(payment_date) start_plan,churn_date from part_plans_cte
  where churn_date is null
  group by customer_id,churn_date
  union all
  select customer_id,dateadd(month,1,start_plan) start_plan,churn_date from all_plans_cte
  where month(start_plan)<12
),all_plans_complete_cte as (
  select cte.customer_id,scte.plan_id,cte.start_plan from all_plans_cte cte
  inner join start_date_plan_cte scte on cte.customer_id=scte.customer_id and cte.start_plan>=scte.start_plan
  where scte.plan_id=(select max(plan_id) from start_date_plan_cte scte2 where cte.customer_id=scte2.customer_id)
  union
  select customer_id,plan_id,payment_date from part_plans_cte
  union
  select customer_id,plan_id,start_plan from churned_plans_cte
)
select cte.customer_id,cte.plan_id,p.plan_name,cte.start_plan payment_date,
  lag(cte.plan_id) over(partition by customer_id order by start_plan) prev_plan,
  lag(cte.start_plan) over(partition by customer_id order by start_plan) prev_payment_date
from all_plans_complete_cte cte
inner join plans p on cte.plan_id=p.plan_id
where year(cte.start_plan)<2021
```
Error in instance customer 16, It must be validated because in "cte" was changed in plan_id (1,2) (Needs correction)
```sql
with cte as (
  select customer_id,plan_id,start_date,
    coalesce(lead(start_date) over(partition by customer_id order by start_date,plan_id),'2020-12-31') start_next_plan 
  from subscriptions
  where customer_id in (1,2,13,15,16,18,19)
  union all
  select customer_id,plan_id,dateadd(month,1,start_date) start_date,start_next_plan from cte
  where dateadd(month,1,start_date)<start_next_plan
),anual_subs as (
  select customer_id,plan_id,start_date,row_number() over(partition by customer_id order by start_date) rn from cte
  where plan_id=3
),monthly_subs as (
  select customer_id,plan_id,start_date from cte
  where plan_id in (1,2) and year(start_date)=2020
),data_cte as (
  select customer_id,plan_id,start_date from monthly_subs
  union
  select customer_id,plan_id,start_date from anual_subs
  where rn=1
),preparing_data as (
  select data.customer_id,p.plan_id,p.plan_name,data.start_date payment_date,
    lag(p.plan_id) over(partition by data.customer_id order by data.start_date) prev_plan,
    dateadd(month,1,lag(data.start_date) over(partition by data.customer_id order by data.start_date)) end_prev_plan_date,
    p.price,
    lag(p.price) over(partition by data.customer_id order by data.start_date) prev_payment
  from data_cte data
  inner join plans p on data.plan_id=p.plan_id
)
select customer_id,plan_id,plan_name,payment_date,
  case when plan_id>prev_plan and payment_date<end_prev_plan_date then price-prev_payment else price end amount,
  row_number() over(partition by customer_id order by payment_date) payment_order
from preparing_data
```
### <p align="center">D. Outside The Box Questions
The following are open ended questions which might be asked during a technical interview for this case study - there are no right or wrong answers, but answers that make sense from both a technical and a business perspective make an amazing impression!

#### 1.How would you calculate the rate of growth for Foodie-Fi?
##### Solution 1:
```sql
with cte as (
  select year(start_date) year,month(start_date) month,count(plan_id) nro_plans from subscriptions
  where plan_id not in (0,4)
  group by year(start_date),month(start_date)
)
select *,
  round((nro_plans-lag(nro_plans) over(order by year,month))*100.0/lag(nro_plans) over(order by year,month),2) growth 
from cte
```
##### Solution 2:
```sql
with cte as (
  select year(s.start_date) year,month(s.start_date) month,p.price from subscriptions s
  inner join plans p on s.plan_id = p.plan_id
)
select year,
  coalesce([1],0) '1',coalesce([2],0) '2',coalesce([3],0) '3',coalesce([4],0) '4',coalesce([5],0) '5',coalesce([6],0) '6',
  coalesce([7],0) '7',coalesce([8],0) '8',coalesce([9],0) '9',coalesce([10],0) '10',coalesce([11],0) '11',coalesce([12],0) '12'
from cte
pivot(
  sum(price)
  for month in ([1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12])
) as p
```
#### 2.What key metrics would you recommend Foodie-Fi management to track over time to assess performance of their overall business?
```sql
with cte as (
  select year(s.start_date) year,month(s.start_date) month,s.plan_id,p.plan_name,p.price from subscriptions s
  inner join plans p on s.plan_id = p.plan_id
  where p.plan_id not in (0,4)
)
select year,month,max([basic monthly]) [basic monthly],max([pro monthly]) [pro monthly],max([pro annual]) [pro annual] --en este caso los corchetes [] sno obligatorios debido a que el nombre de la columna son 2 palabras separadas por espacio
from cte
pivot(
  sum(price)
  for plan_name in ([basic monthly],[pro monthly],[pro annual]) --los corchetes [] son obligatorios en esta parte,
) as p
group by year,month
order by 1,2
```
#### 3.What are some key customer journeys or experiences that you would analyse further to improve customer retention?


#### 4.If the Foodie-Fi team were to create an exit survey shown to customers who wish to cancel their subscription, what questions would you include in the survey?
#### 5.What business levers could the Foodie-Fi team use to reduce the customer churn rate? How would you validate the effectiveness of your ideas?

