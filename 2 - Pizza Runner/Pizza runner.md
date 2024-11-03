# <p align="center" style="margin-top: 0px;">🍜 Case Study #2: Pizza Runner 
## <p align="center"><img src="" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-2/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Did you know that over 115 million kilograms of pizza is consumed daily worldwide??? (Well according to Wikipedia anyway…)

Danny was scrolling through his Instagram feed when something really caught his eye - “80s Retro Styling and Pizza Is The Future!”

Danny was sold on the idea, but he knew that pizza alone was not going to help him get seed funding to expand his new Pizza Empire - so he had one more genius idea to combine with it - he was going to Uberize it - and so Pizza Runner was launched!

Danny started by recruiting “runners” to deliver fresh pizza from Pizza Runner Headquarters (otherwise known as Danny’s house) and also maxed out his credit card to pay freelance developers to build a mobile app to accept orders from customers.

## <p align="center">Questions
This case study has LOTS of questions - they are broken up by area of focus including:

- Pizza Metrics
- Runner and Customer Experience
- Ingredient Optimisation
- Pricing and Ratings
- Bonus DML Challenges (DML = Data Manipulation Language)

Each of the following case study questions can be answered using a single SQL statement.
Again, there are many questions in this case study - please feel free to pick and choose which ones you’d like to try!
Before you start writing your SQL queries however - you might want to investigate the data, you may want to do something with some of those null values and data types in the customer_orders and runner_orders tables!

### <p align="center">A. Pizza Metrics
#### 1.How many pizzas were ordered?
```sql
select count(pizza_id) total_pizzas_ordered from customer_orders;
```
#### 2.How many unique customer orders were made?
```sql
select count(distinct customer_id) nro_customers from customer_orders;
```
#### 3.How many successful orders were delivered by each runner?
```sql
update runner_orders set cancellation = case when cancellation='' then null
                                              when UPPER(cancellation)='NULL' then null
                                              else cancellation end;
select runner_id,count(distinct order_id) orders_delivered from runner_orders
where cancellation is null
group by runner_id
```
#### 4.How many of each type of pizza was delivered?
```sql
alter table customer_orders alter column order_id integer;
alter table customer_orders alter column pizza_id integer;
alter table runner_orders alter column order_id integer;
alter table runner_orders alter column runner_id integer;
alter table pizza_names alter column pizza_name varchar(15);

select p.pizza_name,count(co.pizza_id) nro_pizza_delivered from customer_orders co
inner join pizza_names p on co.pizza_id=p.pizza_id
inner join runner_orders ro on co.order_id=ro.order_id
where ro.cancellation is null
group by p.pizza_name
```
#### 5.How many Vegetarian and Meatlovers were ordered by each customer?
```sql
select c.customer_id,
  sum(case when p.pizza_name="Meatlovers" then 1 else 0 end) Meatlovers,
  sum(case when p.pizza_name="Vegetarian" then 1 else 0 end) Vegetarian
from customer_orders c
inner join pizza_names p on c.pizza_id=p.pizza_id
group by c.customer_id
order by c.customer_id
```
#### 6.What was the maximum number of pizzas delivered in a single order?
```sql
select c.order_id,count(c.pizza_id) nro_pizza_delivered from customer_orders c
inner join runner_orders r on c.order_id=r.order_id
where r.cancellation is null
group by c.order_id
order by 2 desc
```
#### 7.For each customer, how many delivered pizzas had at least 1 change and how many had no changes?
```sql
update customer_orders set exclusions = case when exclusions = '' then null
                                              when UPPER(exclusions)='NULL' then null
                                              else exclusions end;
update customer_orders set extras = case when extras = '' then null
                                              when UPPER(extras)='NULL' then null
                                              else extras end;                                              
select customer_id,
  sum(case when exclusions is not null or extras is not null then 1 else 0 end) with_changes,
    sum(case when exclusions is null and extras is null then 1 else 0 end) no_changes
from customer_orders c
inner join runner_orders r on c.order_id = r.order_id
where r.cancellation is null
group by customer_id
```
#### 8.How many pizzas were delivered that had both exclusions and extras?
```sql
select customer_id,
  sum(case when exclusions is not null and extras is not null then 1 else 0 end) both_changes
from customer_orders c
inner join runner_orders r on c.order_id = r.order_id
where r.cancellation is null
group by customer_id
```
#### 9.What was the total volume of pizzas ordered for each hour of the day?
```sql
with hour_cte as (
  select 0 as hour_order_time
  union all
  select hour_order_time+1 from hour_cte
  where hour_order_time<24
)
select hcte.hour_order_time,count(c.pizza_id) nro_pizzas from customer_orders c
right join hour_cte hcte on datepart(hour,c.order_time)=hcte.hour_order_time
group by hcte.hour_order_time
```
#### 10.What was the volume of orders for each day of the week?
```sql
select datepart(weekday,order_time) date_num,datename(weekday,order_time) date_name,count(distinct order_id) nro_orders from customer_orders
group by datename(weekday,order_time),datepart(weekday,order_time)
order by datepart(weekday,order_time)
```
### <p align="center">B. Runner and Customer Experience
#### 1.How many runners signed up for each 1 week period? (i.e. week starts 2021-01-01)
```sql
select datepart(week,registration_date) week,count(runner_id) nro_runners from runners
group by datepart(week,registration_date)
order by 1
```
#### 2.What was the average time in minutes it took for each runner to arrive at the Pizza Runner HQ to pickup the order?
```sqlwith cte as (
  select datediff(minute,c.order_time,r.pickup_time) time_preparation_order,r.runner_id from customer_orders c
  inner join runner_orders r on c.order_id = r.order_id
  where r.cancellation is null
)
select runner_id,round(avg(time_preparation_order*1.0),2) avg_arrive from cte
group by runner_id
order by 1
```
#### 3.Is there any relationship between the number of pizzas and how long the order takes to prepare?
```sql
update runner_orders set pickup_time = case when UPPER(pickup_time)='NULL' then null else pickup_time end;
alter table runner_orders alter column pickup_time datetime;

with cte as (
  select datediff(minute,c.order_time,r.pickup_time) time_preparation_order,r.order_id,c.pizza_id from customer_orders c
  inner join runner_orders r on c.order_id = r.order_id
  where r.cancellation is null
)
select order_id,time_preparation_order,count(pizza_id) nro_pizzas from cte
group by order_id,time_preparation_order
order by 1
```
 . R: El tiempo de preparación de una pizza suele ser 10 minutos y al ordenar más cantidades el tiempo suele subir en una proporción aproximadamente equivalente, excepto en la orden 8
#### 4.What was the average distance travelled for each customer?
```sql
update runner_orders set distance=case when UPPER(distance)='NULL' then null else distance end;

with cte as (
  select c.customer_id,c.order_id,
    distance,case when charindex('k',distance)!=0 then charindex('k',distance) else len(distance)+1 end flag_index
  from customer_orders c
  inner join runner_orders r on c.order_id = r.order_id
  where cancellation is null
)
select customer_id,avg(cast(left(distance,flag_index-1) as decimal(3,1))) as distance_km from cte
group by customer_id
order by 1
```
#### 5.What was the difference between the longest and shortest delivery times for all orders?
```sql
update runner_orders set duration=case when UPPER(duration)='NULL' then null else duration end;

select max(cast(left(duration,2) as int))-min(cast(left(duration,2) as int)) diff_max_min_duration from runner_orders
where cancellation is null
```
#### 6.What was the average speed for each runner for each delivery and do you notice any trend for these values?
```sql
with cte as (
  select runner_id,pickup_time,
    case when charindex('k',distance)!=0 then charindex('k',distance) else len(distance)+1 end flag_index,
    distance,duration,order_id
  from runner_orders
  where cancellation is null
),speed_cte as (
  select runner_id,order_id,pickup_time,
  cast(left(distance,flag_index-1) as decimal(3,1)) distance,cast(left(duration,2) as int)*60 duration_secs from cte
)
select runner_id,order_id,pickup_time,distance*1000/duration_secs speed_ms from speed_cte
order by 1,3
```
 . R: Se puede notar que todos los runners empiezan con una velocidad lenta al repartir los primeros dias y mientras trancurre los dias su velocidad va aumentando
#### 7.What is the successful delivery percentage for each runner?
```sql
with cte as (
  select runner_id,
    sum(case when cancellation is null then 1 else 0 end) as nro_successful_delivery,
    count(runner_id) total_delivery from runner_orders
  group by runner_id
)
select runner_id,nro_successful_delivery*100.0/total_delivery successful_delivery_percentage from cte
```

### <p align="center"> C. Ingredient Optimisation
#### 1.What are the standard ingredients for each pizza?
```sql
with pizza_recipes_cte as (
  select pizza_id,value as topping from pizza_recipes
  cross apply string_split(replace(toppings,' ',''),',') r
)
select pcte.pizza_id,string_agg(pt.topping_name,', ') toppings from pizza_recipes_cte pcte
inner join pizza_toppings pt on pcte.topping=pt.topping_id
group by pcte.pizza_id
```
#### 2.What was the most commonly added extra?
```sql
with cte as (
    select value as extra_topping from customer_orders 
    cross apply string_split(replace(extras,' ',''),',') as s 
)
select extra_topping as extras,count(extra_topping) times_extras from cte
group by extra_topping
```
#### 3.What was the most common exclusion?
```sql
with cte as (
    select value as exclude_topping from customer_orders 
    cross apply string_split(replace(exclusions,' ',''),',') as s 
)
select exclude_topping as exclusions,count(exclude_topping) times_exclusions from cte
group by exclude_topping
```
#### 4.Generate an order item for each record in the customers_orders table in the format of one of the following:
  - Meat Lovers
  - Meat Lovers - Exclude Beef
  - Meat Lovers - Extra Bacon
  - Meat Lovers - Exclude Cheese, Bacon - Extra Mushroom, Peppers*/
```sql
alter table pizza_toppings alter column topping_name varchar(15);

with exclusion_extra_toppings as (
  select order_id,customer_id,pizza_id,exclusions,extras,
    cast(coalesce(exc.value,exclusions) as int) exclude_topping,
    cast(coalesce(ext.value,extras) as int) extra_topping from customer_orders 
  cross apply string_split(replace(exclusions,' ',''),',') as exc
  cross apply string_split(replace(extras,' ',''),',') as ext
  union all
  select order_id,customer_id,pizza_id,exclusions,extras,
    cast(coalesce(exclusions,null) as int) exclude_topping,
    cast(coalesce(extras,null) as int) extra_topping from customer_orders
  where extras is null or exclusions is null
),exclude_toppings_cte as (
  select distinct cte.order_id,cte.customer_id,cte.pizza_id,cte.exclude_topping,p1.topping_name from exclusion_extra_toppings cte
  left join pizza_toppings p1 on cte.exclude_topping=p1.topping_id
  inner join runner_orders r on cte.order_id=r.order_id
  where cte.exclude_topping is not null
),extra_toppings_cte as (
  select distinct cte.order_id,cte.customer_id,cte.pizza_id,cte.extra_topping,p1.topping_name from exclusion_extra_toppings cte
  left join pizza_toppings p1 on cte.extra_topping=p1.topping_id
  inner join runner_orders r on cte.order_id=r.order_id
  where cte.extra_topping is not null
),exclude_topping_names as (
  select order_id,customer_id,pizza_id,
    string_agg(exclude_topping,', ') within group (order by exclude_topping) exclude_toppings,
    string_agg(topping_name,', ') within group (order by exclude_topping) exclude_topping_names from exclude_toppings_cte
  group by order_id,customer_id,pizza_id
),extra_topping_names as (
  select order_id,customer_id,pizza_id,
    string_agg(extra_topping,', ') within group (order by extra_topping) extra_toppings,
    string_agg(topping_name,', ') within group (order by extra_topping) extra_topping_names from extra_toppings_cte
  group by order_id,customer_id,pizza_id
),final_cte as (
  select c.order_id,c.customer_id,c.pizza_id,c.exclusions,c.extras,
    case when c.pizza_id=1 then 'Meat Lovers' else 'Vegetarian' end type_customer,
    "Exclude "+exc.exclude_topping_names exclude_flag,"Extra "+ext.extra_topping_names extra_flag from customer_orders c
  left join exclude_topping_names exc on c.order_id=exc.order_id and c.customer_id=exc.customer_id and c.pizza_id=exc.pizza_id
  left join extra_topping_names ext on c.order_id=ext.order_id and c.customer_id=ext.customer_id and c.pizza_id=ext.pizza_id
)
select order_id,customer_id,pizza_id,exclusions,extras,
  CONCAT_WS(' - ',NULLIF(type_customer,''),NULLIF(exclude_flag,''),NULLIF(extra_flag,'')) format_flag from final_cte
order by order_id
```
#### 5.Generate an alphabetically ordered comma separated ingredient list for each pizza order from the customer_orders table and add a 2x in front of any relevant ingredients
  For example: "Meat Lovers: 2xBacon, Beef, ... , Salami"*/
```sql
alter table pizza_recipes alter column toppings varchar(25);

with customer_orders_rn as (
  select row_number() over(order by order_id) rn,* from customer_orders
),exclusion_extra_toppings as (
  select rn,order_id,customer_id,pizza_id,exclusions,extras,
    coalesce(exc.value,exclusions,null) exclude_topping,
    coalesce(ext.value,extras,null) extra_topping from customer_orders_rn 
  cross apply string_split(replace(exclusions,' ',''),',') as exc
  cross apply string_split(replace(extras,' ',''),',') as ext
  union all
  select rn,order_id,customer_id,pizza_id,exclusions,extras,
    coalesce(exclusions,null) exclude_topping,
    coalesce(extras,null) extra_topping from customer_orders_rn
  where exclusions is null or extras is null
),toppings_cte as (
  select pizza_id,toppings,cast(value as int) as topping from pizza_recipes 
  cross apply string_split(replace(toppings,' ',''),',') as s 
),all_ingredients_cte as (
  select c.rn,c.order_id,c.customer_id,c.pizza_id,t.topping all_ingredients from customer_orders_rn c
  inner join toppings_cte t on c.pizza_id=t.pizza_id
  where t.topping not in (select distinct c1.exclude_topping from exclusion_extra_toppings c1
                          where c.rn=c1.rn and c.order_id=c1.order_id and c.customer_id=c1.customer_id 
                          and c.pizza_id=c1.pizza_id and exclude_topping is not null)
  union all
  select distinct rn,order_id,customer_id,pizza_id,cast(extra_topping as int) all_ingredients from exclusion_extra_toppings
  where extra_topping is not null
),final_cte as (
  select cte.*,t.topping_name,count(all_ingredients) nro_ingredients from all_ingredients_cte cte
  inner join pizza_toppings t on cte.all_ingredients=t.topping_id
  group by rn,order_id,customer_id,pizza_id,all_ingredients,t.topping_name
)
select order_id,customer_id,pizza_id,
  string_agg(case when nro_ingredients=1 then topping_name else concat(nro_ingredients,'x',topping_name) end,', ') within group (order by topping_name) format_flag 
from final_cte
group by rn,order_id,customer_id,pizza_id
order by 1,2,3,4
```
#### 6.What is the total quantity of each ingredient used in all delivered pizzas sorted by most frequent first?
```sql
with customer_orders_rn as (
  select row_number() over(order by order_id) rn,* from customer_orders
),exclusion_extra_toppings as (
  select rn,order_id,customer_id,pizza_id,exclusions,extras,
    coalesce(exc.value,exclusions,null) exclude_topping,
    coalesce(ext.value,extras,null) extra_topping from customer_orders_rn 
  cross apply string_split(replace(exclusions,' ',''),',') as exc
  cross apply string_split(replace(extras,' ',''),',') as ext
  union all
  select rn,order_id,customer_id,pizza_id,exclusions,extras,
    coalesce(exclusions,null) exclude_topping,
    coalesce(extras,null) extra_topping from customer_orders_rn
  where exclusions is null or extras is null
),toppings_cte as (
  select pizza_id,toppings,cast(value as int) as topping from pizza_recipes 
  cross apply string_split(replace(toppings,' ',''),',') as s 
),all_ingredients_cte as (
  select c.rn,c.order_id,c.customer_id,c.pizza_id,t.topping all_ingredients from customer_orders_rn c
  inner join toppings_cte t on c.pizza_id=t.pizza_id
  where t.topping not in (select distinct c1.exclude_topping from exclusion_extra_toppings c1
                          where c.rn=c1.rn and c.order_id=c1.order_id and c.customer_id=c1.customer_id 
                          and c.pizza_id=c1.pizza_id and exclude_topping is not null)
  union all
  select distinct rn,order_id,customer_id,pizza_id,cast(extra_topping as int) all_ingredients from exclusion_extra_toppings
  where extra_topping is not null
)
select cte.all_ingredients,count(cte.all_ingredients) nro_ingredients from all_ingredients_cte cte
inner join runner_orders r on cte.order_id=r.order_id
where r.cancellation is null
group by cte.all_ingredients
order by 2 desc,1
```

### <p align="center">D. Pricing and Ratings
#### 1.If a Meat Lovers pizza costs $12 and Vegetarian costs $10 and there were no charges for changes - how much money has Pizza Runner made so far if there are no delivery fees?
```sql
select sum(case when pizza_id=1 then 12 else 10 end) revenue from customer_orders c 
inner join runner_orders r on c.order_id = r.order_id
where r.cancellation is null
```
#### 2.What if there was an additional $1 charge for any pizza extras?
  - Add cheese is $1 extra*/
```sql
with price_with_extra as (
  select c.order_id,pizza_id,case when pizza_id=1 then 12 else 10 end price,extras,coalesce(len(extras)-len(replace(extras,',',''))+1,0) nro_extras from customer_orders c 
  inner join runner_orders r on c.order_id = r.order_id
  where r.cancellation is null 
)
select sum(price+nro_extras) revenue from price_with_extra
```
#### 3.The Pizza Runner team now wants to add an additional ratings system that allows customers to rate their runner, how would you design an additional table for this new dataset - generate a schema for this new table and insert your own data for ratings for each successful customer order between 1 to 5.
```sql
drop table if exists runner_rating;
create table runner_ratings (
  order_id integer,
  runner_id integer,
  rating int
)

insert into runner_ratings values
  (1,1,2),
  (2,1,2),
  (3,1,2),
  (4,2,1),
  (5,3,2),
  (6,3,null),
  (7,2,3),
  (8,2,5),
  (9,2,null),
  (10,1,3);

select * from runner_ratings
```
#### 4.Using your newly generated table - can you join all of the information together to form a table which has the following information for successful deliveries?
  - customer_id
  - order_id
  - runner_id
  - rating
  - order_time
  - pickup_time
  - Time between order and pickup
  - Delivery duration
  - Average speed
  - Total number of pizzas*/
```sql
with cte as (
  select runner_id,case when charindex('k',distance)!=0 then charindex('k',distance) else len(distance)+1 end flag_index,
    distance,duration,order_id
  from runner_orders
  where cancellation is null
),cte2 as (
  select runner_id,order_id,cast(left(distance,flag_index-1) as decimal(3,1)) distance,cast(left(duration,2) as int)*60 duration_secs from cte
),speed_cte as (
  select runner_id,order_id,distance*1000/duration_secs speed_ms from cte2
),request_cte as (
  select c.customer_id,c.order_id,ro.runner_id,rr.rating,c.order_time,ro.pickup_time,
  datediff(minute,c.order_time,ro.pickup_time) time_btw_order_pickup,cast(left(ro.duration,2) as int) duration_mins,pizza_id
  from customer_orders c
  inner join runner_orders ro on c.order_id = ro.order_id
  inner join runner_ratings rr on ro.order_id=rr.order_id and ro.runner_id=rr.runner_id
  where ro.cancellation is null
)
select cte1.customer_id,cte1.order_id,cte1.runner_id,cte1.rating,cte1.order_time,cte1.pickup_time,cte1.duration_mins,
  avg(s.speed_ms) avg_speed,count(cte1.pizza_id) nro_pizzas from request_cte cte1
inner join speed_cte s on cte1.order_id=s.order_id and cte1.runner_id=s.runner_id
group by cte1.customer_id,cte1.order_id,cte1.runner_id,cte1.rating,cte1.order_time,cte1.pickup_time,cte1.duration_mins
order by 2
```
#### 5.If a Meat Lovers pizza was $12 and Vegetarian $10 fixed prices with no cost for extras and each runner is paid $0.30 per kilometre traveled - how much money does Pizza Runner have left over after these deliveries?
```sql
with cte as (
  select runner_id,order_id,
    distance,case when charindex('k',distance)!=0 then charindex('k',distance) else len(distance)+1 end flag_index
  from runner_orders 
  where cancellation is null
),runner_delivery_cost_cte as (
  select order_id,runner_id,cast(left(distance,flag_index-1) as decimal(3,1))*0.3 as runner_delivery_cost from cte
),request_cte as (
  select c.order_id,sum(case when c.pizza_id=1 then 12 else 10 end) price,rc.runner_delivery_cost from customer_orders c
  inner join runner_orders r on c.order_id = r.order_id
  inner join runner_delivery_cost_cte rc on r.order_id=rc.order_id and r.runner_id=rc.runner_id
  where r.cancellation is null
  group by c.order_id,rc.runner_delivery_cost
)
select sum(price-runner_delivery_cost) revenue from request_cte
```
### <p align="center">E. Bonus Questions
#### 1.If Danny wants to expand his range of pizzas - how would this impact the existing data design? Write an INSERT statement to demonstrate what would happen if a new Supreme pizza with all the toppings was added to the Pizza Runner menu?
```sql
alter table pizza_recipes alter column toppings varchar(50);
insert into pizza_recipes(pizza_id,toppings) select 3 pizza_id,string_agg(topping_id,', ') from pizza_toppings
insert into pizza_names values(3,'Supreme Pizza');
```