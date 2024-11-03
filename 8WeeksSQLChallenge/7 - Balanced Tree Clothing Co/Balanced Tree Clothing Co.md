# <p align="center" style="margin-top: 0px;">Case Study #7: Balanced Tree Clothing Co
## <p align="center"><img src="https://github.com/DevR-Z/SQL-CaseStudies/blob/main/8WeeksSQLChallenge/7%20-%20Balanced%20Tree%20Clothing%20Co/resources/c7.png?raw=true" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-7/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Balanced Tree Clothing Company prides themselves on providing an optimised range of clothing and lifestyle wear for the modern adventurer!
Danny, the CEO of this trendy fashion company has asked you to assist the team’s merchandising teams analyse their sales performance and generate a basic financial report to share with the wider business.

## <p align="center">Questions
The following questions can be considered key business questions and metrics that the Balanced Tree team requires for their monthly reports.
Each question can be answered using a single query - but as you are writing the SQL to solve each individual problem, keep in mind how you would generate all of these metrics in a single SQL script which the Balanced Tree team can run each month.

### <p align="center">A. High Level Sales Analysis
#### 1.What was the total quantity sold for all products?
```sql
select sum(qty) total_sold from sales
```
#### 2.What is the total generated revenue for all products before discounts?
```sql
select sum(qty*price) total_sold from sales
```
#### 3.What was the total discount amount for all products?
```sql
select sum(qty*price - discount) total_sold_with_dsct from sales
```
### <p align="center">B. Transaction Analysis
#### 1.How many unique transactions were there?
```sql
select count(distinct txn_id) nro_txns from sales
```
#### 2.What is the average unique products purchased in each transaction?
```sql
with nro_products as (
  select txn_id,count(distinct prod_id) nro_products from sales
  group by txn_id
)
select round(avg(nro_products*1.0),0) avg_prod_purchased from nro_products
```
#### 3.What are the 25th, 50th and 75th percentile values for the revenue per transaction?
```sql
with revenue as (
  select txn_id,sum(qty*price - discount) revenue from sales
  group by txn_id
)
select distinct percentile_cont(0.25) within group (order by revenue) over() prct_25,
  percentile_cont(0.5) within group (order by revenue) over() prct_50,
  percentile_cont(0.75) within group (order by revenue) over() prct_75
from revenue
```
#### 4.What is the average discount value per transaction?
```sql
with total_dsct as (
  select txn_id,sum(discount) total_dsct from sales
  group by txn_id
)
select round(avg(total_dsct*1.0),0) avg_dsct from total_dsct
```
#### 5.What is the percentage split of all transactions for members vs non-members?
```sql
select member,count(distinct txn_id) nro_txns,
  round(count(distinct txn_id)*100.0/(select count(distinct txn_id) from sales),2) percentage from sales
group by member
```
#### 6.What is the average revenue for member transactions and non-member transactions?
```sql
select member,sum(qty*price-discount) revenue,
  round(sum(qty*price-discount)*100.0/(select sum(qty*price-discount) from sales),2) percentage from sales
group by member
```
### <p align="center">C. Product Analysis
#### 1.What are the top 3 products by total revenue before discount?
```sql
select top 3 prod_id,sum(qty*price) total_revenue from sales
group by prod_id
order by 2 desc
```
#### 2.What is the total quantity, revenue and discount for each segment?
```sql
select p.segment_id,sum(s.qty) total_quantity,sum(s.qty*s.price) total_revenue,sum(s.discount) total_discount from sales s
inner join product_details p on s.prod_id=p.product_id
group by p.segment_id
```
#### 3.What is the top selling product for each segment?
```sql
with quantity_rnk as (
  select p.segment_id,s.prod_id,sum(s.qty) total_quantity,
    rank() over(partition by p.segment_id order by sum(s.qty) desc) rnk
  from sales s
  inner join product_details p on s.prod_id=p.product_id
  group by p.segment_id,s.prod_id
)
select * from quantity_rnk where rnk=1
```
#### 4.What is the total quantity, revenue and discount for each category?
```sql
select p.category_id,sum(s.qty) total_quantity,sum(s.qty*s.price) total_revenue,sum(s.discount) total_discount from sales s
inner join product_details p on s.prod_id=p.product_id
group by p.category_id
```
#### 5.What is the top selling product for each category?
```sql
with quantity_rnk as (
  select p.category_id,s.prod_id,sum(s.qty) total_quantity,
    rank() over(partition by p.category_id order by sum(s.qty) desc) rnk
  from sales s
  inner join product_details p on s.prod_id=p.product_id
  group by p.category_id,s.prod_id
)
select * from quantity_rnk where rnk=1
```
#### 6.What is the percentage split of revenue by product for each segment?
```sql
select p.segment_id,s.prod_id,sum(s.qty*s.price-s.discount) revenue,
  round(sum(s.qty*s.price-s.discount)*100.0/(select sum(s1.qty*s1.price-s1.discount) from sales s1
                                  inner join product_details p1 on s1.prod_id=p1.product_id
                                  where p1.segment_id=p.segment_id
                                  group by p1.segment_id),2) percentage
from sales s
inner join product_details p on s.prod_id=p.product_id
group by p.segment_id,s.prod_id
```
#### 7.What is the percentage split of revenue by segment for each category?
```sql
select p.category_id,p.segment_id,sum(s.qty*s.price-s.discount) revenue,
  round(sum(s.qty*s.price-s.discount)*100.0/(select sum(s1.qty*s1.price-s1.discount) from sales s1
                                  inner join product_details p1 on s1.prod_id=p1.product_id
                                  where p1.category_id=p.category_id
                                  group by p1.category_id),2) percentage
from sales s
inner join product_details p on s.prod_id=p.product_id
group by p.category_id,p.segment_id
```
#### 8.What is the percentage split of total revenue by category?
```sql
select p.category_id,sum(s.qty*s.price-s.discount) revenue,
  round(sum(s.qty*s.price-s.discount)*100.0/(select sum(qty*price-discount) from sales),2) percentage
from sales s
inner join product_details p on s.prod_id=p.product_id
group by p.category_id
```
#### 9.What is the total transaction “penetration” for each product? (hint: penetration = number of transactions where at least 1 quantity of a product was purchased divided by total number of transactions)
```sql
select prod_id,count(distinct txn_id) nro_txns,
  round(count(distinct txn_id)*100.0/(select count(distinct txn_id) from sales),2) penetration
from sales
group by prod_id
```
#### 10.What is the most common combination of at least 1 quantity of any 3 products in a 1 single transaction?
```sql
with nro_combinations as (
  select s1.prod_id p1,s2.prod_id p2,s3.prod_id p3,count(distinct s1.txn_id) nro_combinations from sales s1
  inner join sales s2 on s1.txn_id=s2.txn_id and s1.prod_id!=s2.prod_id
  inner join sales s3 on s1.txn_id=s3.txn_id and s1.prod_id!=s3.prod_id and s2.prod_id!=s3.prod_id
  group by s1.prod_id,s2.prod_id,s3.prod_id
),all_combinations as (
  select distinct case when p1<=p2 and p1<=p3 then p1
              when p2<=p1 and p2<=p3 then p2
              else p3 end p1,
         case when (p1<=p2 and p1>p3) or (p1>p2 and p1<=p3) then p1
              when (p2<=p1 and p2>p3) or (p2>p1 and p2<=p3) then p2
              else p3 end p2,
         case when p1>=p2 and p1>=p3 then p1
              when p2>=p1 and p2>=p3 then p2
              else p3 end p3,
         nro_combinations
  from nro_combinations
)
select *,dense_rank() over(order by nro_combinations desc) d_rnk from all_combinations

SELECT t1.prod_id, t2.prod_id, t3.prod_id, COUNT(*) AS combination_cnt FROM sales t1
JOIN sales t2 ON t1.txn_id = t2.txn_id AND t1.prod_id < t2.prod_id
JOIN sales t3 ON t1.txn_id = t3.txn_id AND t2.prod_id < t3.prod_id
GROUP BY t1.prod_id, t2.prod_id, t3.prod_id
ORDER BY 4 DESC
```
### <p align="center">E. Bonus Challenge
Use a single SQL query to transform the product_hierarchy and product_prices datasets to the product_details table.
Hint: you may want to consider using a recursive CTE to solve this problem!
```sql
with cte as (
  select id as parent_id,level_text parent_level_text,id,0 as lvl,level_text from product_hierarchy
  where parent_id is null
  union all
  select h.parent_id as parent_id,cte.parent_level_text,h.id,lvl+1 as lvl,h.level_text from cte
  inner join product_hierarchy h on cte.id=h.parent_id
)
select p.product_id,p.price,c2.level_text+' '+c1.level_text+' - '+c1.parent_level_text product_name,
  c1.parent_id category_id,c2.parent_id segment_id,c2.id style_id,
  c1.parent_level_text category_name,c1.level_text segment_name,c2.level_text style_name
from cte c1
inner join cte c2 on c1.id=c2.parent_id
inner join product_prices p on c2.id=p.id
where c1.lvl>0 and c2.lvl>0
order by style_id
```
Easier solution without recursive CTE:
```sql
select p.product_id,p.price,h1.level_text+' '+h2.level_text+' - '+h3.level_text product_name,
  h3.id category_id,h2.id segment_id,h1.id style_id,
  h3.level_text category_name,h2.level_text segment_name,h1.level_text style_name 
from product_prices p
inner join product_hierarchy h1 on p.id=h1.id
inner join product_hierarchy h2 on h1.parent_id=h2.id
inner join product_hierarchy h3 on h2.parent_id=h3.id
```