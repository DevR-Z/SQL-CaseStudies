# <p align="center" style="margin-top: 0px;">Case Study #6: Clique Bait
## <p align="center"><img src="https://github.com/DevR-Z/SQL-CaseStudies/blob/main/8WeeksSQLChallenge/6%20-%20Clique%20Bait/resources/c6.png?raw=true" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-6/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Clique Bait is not like your regular online seafood store - the founder and CEO Danny, was also a part of a digital data analytics team and wanted to expand his knowledge into the seafood industry!
In this case study - you are required to support Danny’s vision and analyse his dataset and come up with creative solutions to calculate funnel fallout rates for the Clique Bait online store.

## <p align="center">Questions

### <p align="center">2. Digital Analysis
Using the available datasets - answer the following questions using a single query for each one:
#### 1.How many users are there?
```sql
select count(distinct user_id) nro_users from users;
```
#### 2.How many cookies does each user have on average?
```sql
with cookies_cte as (
  select user_id,count(cookie_id)*1.0 nro_cookies from users
  group by user_id 
)
select round(avg(nro_cookies),0) avg_cookies from cookies_cte
```
#### 3.What is the unique number of visits by all users per month?
```sql
select month(event_time) month,count(distinct e.visit_id) nro_visits from events e
inner join users u on e.cookie_id=u.cookie_id
group by month(event_time)
order by 1
```
#### 4.What is the number of events for each event type?
```sql
select ei.event_name,count(visit_id) nro_events from events e
inner join event_identifier ei on e.event_type=ei.event_type
group by ei.event_name
order by 2 desc
```
#### 5.What is the percentage of visits which have a purchase event?
```sql
with cte as (
  select ei.event_name,count(distinct e.visit_id) nro_visits from events e
  inner join event_identifier ei on e.event_type=ei.event_type
  group by ei.event_name
)
select event_name,nro_visits,
  round(nro_visits*100.0/(select count(distinct visit_id) from events),2) percentage 
from cte where event_name='Purchase'
```
#### 6.What is the percentage of visits which view the checkout page but do not have a purchase event?
```sql
select count(distinct visit_id) nro_visits_flag,
  round(count(distinct visit_id)*100.0/(select count(distinct visit_id) from events),2) percentage from events
where event_type!=3 and page_id=12
order by 1
```
#### 7.What are the top 3 pages by number of views?
```sql
select top 3 p.page_name,sum(case when ei.event_name='Page View' then 1 else 0 end) nro_views from events e
inner join page_hierarchy p on e.page_id=p.page_id
inner join event_identifier ei on e.event_type=ei.event_type
group by p.page_name
order by 2 desc
```
#### 8.What is the number of views and cart adds for each product category?
```sql
select p.product_category,
  sum(case when ei.event_name='Page View' then 1 else 0 end) nro_views,
  sum(case when ei.event_name='Add to Cart' then 1 else 0 end) nro_cart_adds
from events e
inner join page_hierarchy p on e.page_id=p.page_id
inner join event_identifier ei on e.event_type=ei.event_type
where p.product_category is not null
group by p.product_category
order by 2 desc
```
#### 9.What are the top 3 products by purchases?
```sql
select p.product_id,p.page_name,count(e.visit_id) nro_purchases from events e
inner join page_hierarchy p on e.page_id=p.page_id
inner join event_identifier ei on e.event_type=ei.event_type
where visit_id in (select distinct visit_id from events where event_type=3) 
  and p.product_id is not null and e.event_type=2
group by p.product_id,p.page_name
order by 3 desc
```
### <p align="center">3. Product Funnel Analysis
Using a single SQL query - create a new output table which has the following details:
#### 1.How many times was each product viewed?
```sql
select p.product_id,p.page_name,count(e.page_id) nro_views from events e
inner join page_hierarchy p on e.page_id=p.page_id
where p.product_id is not null and event_type=1
group by p.product_id,p.page_name
```
#### 2.How many times was each product added to cart?
```sql
select p.product_id,p.page_name,count(e.page_id) nro_add_carts from events e
inner join page_hierarchy p on e.page_id=p.page_id
where p.product_id is not null and event_type=2
group by p.product_id,p.page_name
```
#### 3.How many times was each product added to a cart but not purchased (abandoned)?
```sql
select p.product_id,p.page_name,count(e.visit_id) nro_abandoned from events e
inner join page_hierarchy p on e.page_id=p.page_id
where p.product_id is not null and event_type=2 
and e.visit_id not in (select distinct visit_id from events
                        where event_type=3)
group by p.product_id,p.page_name
```
#### 4.How many times was each product purchased?
```sql
select p.product_id,p.page_name,count(e.visit_id) nro_purchased from events e
inner join page_hierarchy p on e.page_id=p.page_id
inner join event_identifier ei on e.event_type=ei.event_type
where visit_id in (select distinct visit_id from events where event_type=3) 
and p.product_id is not null and e.event_type=2
group by p.product_id,p.page_name
```
#### Final query
```sql
with viewed as (
  select p.product_id,p.page_name,count(e.page_id) nro_views from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=1
  group by p.product_id,p.page_name
),added_to_cart as (
  select p.product_id,p.page_name,count(e.page_id) nro_add_carts from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=2
  group by p.product_id,p.page_name
),abandoned as (
  select p.product_id,p.page_name,count(e.visit_id) nro_abandoned from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=2 
    and e.visit_id not in (select distinct visit_id from events
                            where event_type=3)
  group by p.product_id,p.page_name
),purchased as (
  select p.product_id,p.page_name,count(e.visit_id) nro_purchased from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  inner join event_identifier ei on e.event_type=ei.event_type
  where visit_id in (select distinct visit_id from events where event_type=3) 
    and p.product_id is not null and e.event_type=2
  group by p.product_id,p.page_name
)
select w.*,ad.nro_add_carts,ab.nro_abandoned,p.nro_purchased into product_data_temp from viewed w
inner join added_to_cart ad on w.product_id=ad.product_id
inner join abandoned ab on w.product_id=ab.product_id
inner join purchased p on w.product_id=p.product_id

select * from product_data_temp
```
#### Additionally, create another table which further aggregates the data for the above points but this time for each product category instead of individual products.
```sql
with viewed as (
  select p.product_category,count(e.page_id) nro_views from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=1
  group by p.product_category
),added_to_cart as (
  select p.product_category,count(e.page_id) nro_add_carts from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=2
  group by p.product_category
),abandoned as (
  select p.product_category,count(e.visit_id) nro_abandoned from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  where p.product_id is not null and event_type=2 
    and e.visit_id not in (select distinct visit_id from events
                            where event_type=3)
  group by p.product_category
),purchased as (
  select p.product_category,count(e.visit_id) nro_purchased from events e
  inner join page_hierarchy p on e.page_id=p.page_id
  inner join event_identifier ei on e.event_type=ei.event_type
  where visit_id in (select distinct visit_id from events where event_type=3) 
    and p.product_id is not null and e.event_type=2
  group by p.product_category
)
select w.*,ad.nro_add_carts,ab.nro_abandoned,p.nro_purchased into category_data_temp from viewed w
inner join added_to_cart ad on w.product_category=ad.product_category
inner join abandoned ab on w.product_category=ab.product_category
inner join purchased p on w.product_category=p.product_category

select * from category_data_temp
```
#### Use your 2 new output tables - answer the following questions:
#### 1.Which product had the most views, cart adds and purchases?
```sql
select (select top 1 page_name from product_data_temp order by nro_views desc) most_viewed,
  (select top 1 page_name from product_data_temp order by nro_add_carts desc) most_cart_added,
  (select top 1 page_name from product_data_temp order by nro_purchased desc) most_purchased
```
#### 2.Which product was most likely to be abandoned?
```sql
select top 1 page_name most_abandoned from product_data_temp order by nro_abandoned desc
```
#### 3.Which product had the highest view to purchase percentage?
```sql
select page_name,nro_views,nro_purchased,round(nro_purchased*100.0/nro_views,2) percentage from product_data_temp
order by 4 desc
```
#### 4.What is the average conversion rate from view to cart add?
```sql
with cte as (
  select page_name,nro_views,nro_add_carts,nro_add_carts*100.0/nro_views percentage from product_data_temp
)
select round(avg(percentage),2) avg_conversion_rate_viewed_added_cart from cte
```
#### 5.What is the average conversion rate from cart add to purchase?
```sql
with cte as (
  select page_name,nro_add_carts,nro_purchased,nro_purchased*100.0/nro_add_carts percentage from product_data_temp
)
select round(avg(percentage),2) avg_conversion_rate_added_cart_purchaed from cte
```
### <p align="center">4. Campaigns Analysis
Generate a table that has 1 single row for every unique visit_id record and has the following columns:
  - user_id
  - visit_id
  - visit_start_time: the earliest event_time for each visit
  - page_views: count of page views for each visit
  - cart_adds: count of product cart add events for each visit
  - purchase: 1/0 flag if a purchase event exists for each visit
  - campaign_name: map the visit to a campaign if the visit_start_time falls between the start_date and end_date
  - impression: count of ad impressions for each visit
  - click: count of ad clicks for each visit
  - (Optional column) cart_products: a comma separated text value with products added to the cart sorted by the order they were added to the cart (hint: use the sequence_number)
```sql
select u.user_id,e.visit_id,min(e.event_time) visit_start_time,
  sum(case when e.event_type=1 then 1 else 0 end) page_views,
  sum(case when e.event_type=2 then 1 else 0 end) cart_adds,
  sum(case when e.event_type=3 then 1 else 0 end) purchase,
  c.campaign_name,
  sum(case when e.event_type=4 then 1 else 0 end) impression,
  sum(case when e.event_type=5 then 1 else 0 end) click,
  coalesce(string_agg(case when p.product_id is not null and e.event_type=2 then p.page_name else null end,',') within group (order by e.sequence_number),'-') cart_products
into analysis_dataset from events e
inner join users u on e.cookie_id=u.cookie_id
inner join campaign_identifier c on e.event_time between c.start_date and c.end_date
inner join page_hierarchy p on e.page_id=p.page_id
group by u.user_id,e.visit_id,c.campaign_name

select * from analysis_datase
```
Use the subsequent dataset to generate at least 5 insights for the Clique Bait team - bonus: prepare a single A4 infographic that the team can use for their management reporting sessions, be sure to emphasise the most important points from your findings.
Some ideas you might want to investigate further include:

#### Identifying users who have received impressions during each campaign period and comparing each metric with other users who did not have an impression event
```sql
select campaign_name,impression,
  round(sum(page_views)*1.0/count(visit_id),2) avg_views_visit,
  round(sum(cart_adds)*1.0/count(visit_id),2) avg_cart_adds_visit,
  round(sum(purchase)*1.0/count(visit_id),2) avg_purchase_visit,
  round(sum(click)*1.0/count(visit_id),2) avg_click_visit
from analysis_dataset
group by campaign_name,impression
order by 1
```
#### Does clicking on an impression lead to higher purchase rates?
```sql
select campaign_name,impression,click,
  round(sum(purchase)*1.0/count(visit_id),2) avg_purchase_visit
from analysis_dataset
group by campaign_name,impression,click
order by 1,2,3 --Al dar click en una impresión si genera mayores tazas de compra
```
#### What is the uplift in purchase rate when comparing users who click on a campaign impression versus users who do not receive an impression? What if we compare them with users who just an impression but do not click?
```sql
with first as (
  select campaign_name,impression,click,
    round(sum(purchase)*1.0/count(visit_id),2) avg_purchase_visit,
    row_number() over(partition by campaign_name order by impression,click) rn
  from analysis_dataset
  where (impression=1 and click = 1) or impression=0
  group by campaign_name,impression,click
),uplift_cte as (
  select campaign_name,
    avg_purchase_visit-lag(avg_purchase_visit) over(partition by campaign_name order by rn) uplift_value 
  from first
)
select * from uplift_cte where uplift_value is not null 
```
```sql
with second as (
  select campaign_name,impression,click,
    round(sum(purchase)*1.0/count(visit_id),2) avg_purchase_visit,
    row_number() over(partition by campaign_name order by impression,click) rn
  from analysis_dataset
  where (impression=1 and click = 1) or (impression=1 and click = 0)
  group by campaign_name,impression,click
),uplift_cte as (
  select campaign_name,
    avg_purchase_visit-lag(avg_purchase_visit) over(partition by campaign_name order by rn) uplift_value 
  from second
)
select * from uplift_cte where uplift_value is not null 
```