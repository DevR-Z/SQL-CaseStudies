# <p align="center" style="margin-top: 0px;">🍜 Case Study #1: Danny's Dinner 
## <p align="center"><img src="" alt="image" width="400" heigth="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-1/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Danny seriously loves Japanese food so in the beginning of 2021, he decides to embark upon a risky venture and opens up a cute little restaurant that sells his 3 favourite foods: sushi, curry and ramen.

Danny’s Diner is in need of your assistance to help the restaurant stay afloat - the restaurant has captured some very basic data from their few months of operation but have no idea how to use their data to help them run the business.

## <p align="center">Questions

#### 1. What is the total amount each customer spent at the restaurant?
```sql
select s.customer_id,sum(m.price) total_spent from sales s
inner join menu m on s.product_id = m.product_id
group by s.customer_id
```
#### 2. How many days has each customer visited the restaurant?
```sql
select customer_id,count(distinct order_date) days_visited from sales
group by customer_id
```
#### 3. What was the first item from the menu purchased by each customer?
```sql
with cte as (
  select s.customer_id,s.order_date,m.product_name,row_number() over(partition by s.customer_id order by s.order_date) rn
  from sales s
  inner join menu m on s.product_id = m.product_id
)
select customer_id,product_name first_menu from cte
where rn=1
```

#### 4.What is the most purchased item on the menu and how many times was it purchased by all customers?
```sql
with cte as (
  select s.customer_id,m.product_name,count(m.product_name) times_purchased,
    rank() over(partition by s.customer_id order by count(m.product_name) desc) rnk
  from sales s
  inner join menu m on s.product_id = m.product_id
  group by s.customer_id,m.product_name
)
select customer_id,product_name,times_purchased from cte where rnk=1
```
#### 5.Which item was the most popular for each customer?
```sql
with cte as (
  select s.customer_id,m.product_name,count(m.product_name) times_purchased,
    rank() over(partition by s.customer_id order by count(m.product_name) desc) rnk
  from sales s
  inner join menu m on s.product_id = m.product_id
  group by s.customer_id,m.product_name
)
select customer_id,product_name from cte where rnk=1
```
#### 6.Which item was purchased first by the customer after they became a member?
```sql
with cte as (
  select s.customer_id,menu.product_name,rank() over(partition by s.customer_id order by s.order_date) rnk from sales s
  inner join members m on s.customer_id=m.customer_id and s.order_date>=m.join_date
  inner join menu on s.product_id=menu.product_id
)
select customer_id,product_name from cte where rnk=1
```
#### 7.Which item was purchased just before the customer became a member?
```sql
with cte as (
  select s.customer_id,max(s.order_date) max_date from sales s
  inner join members m on s.customer_id=m.customer_id and s.order_date<=m.join_date
  group by s.customer_id
)
select s.customer_id,m.product_name item_bef_memb from sales s
inner join cte c on s.customer_id=c.customer_id and s.order_date=c.max_date
inner join menu m on s.product_id=m.product_id
```
#### 8.What is the total items and amount spent for each member before they became a member?
```sql
select s.customer_id,count(s.product_id) total_items,sum(menu.price) total_spent from sales s
inner join members m on s.customer_id=m.customer_id and s.order_date<=m.join_date
inner join menu on s.product_id=menu.product_id
group by s.customer_id
```
#### 9.If each $1 spent equates to 10 points and sushi has a 2x points multiplier - how many points would each customer have?
```sql
with cte as (
  select s.customer_id,s.order_date,m.product_name,
    row_number() over(partition by customer_id order by order_date) rn,
    case when m.product_name="sushi" then 0 else m.price*10 end points
  from sales s
  inner join menu m on s.product_id = m.product_id
),cte2 as (
  select rn,customer_id,order_date,product_name,points,points total_points from cte
  where rn=1
  union all
  select cte.rn,cte.customer_id,cte.order_date,cte.product_name,cte.points,
    case when cte.product_name="sushi" then total_points*2 else total_points+cte.points end total_points
  from cte2
  inner join cte on cte2.customer_id=cte.customer_id and cte2.rn+1=cte.rn
),last_points_cte as (
  select customer_id,max(rn) max_rn from cte2
  group by customer_id
)
select cte2.customer_id,cte2.total_points from cte2
inner join last_points_cte lcte on cte2.rn=lcte.max_rn and cte2.customer_id=lcte.customer_id
order by cte2.customer_id
```
#### 10.In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi - how many points do customer A and B have at the end of January?
```sql
with cte as (
  select s.customer_id,s.order_date,me.price*10 points,m.join_date,
    row_number() over(partition by s.customer_id order by s.order_date) rn from sales s
  inner join members m on s.customer_id = m.customer_id
  inner join menu me on s.product_id = me.product_id
),cte2 as (
  select rn,customer_id,order_date,join_date,points,datediff(day,join_date,order_date) as diff,points total_points from cte
  where rn=1
  union all
  select cte.rn,cte.customer_id,cte.order_date,cte.join_date,cte.points,datediff(day,cte.join_date,cte.order_date) diff,
    case when datediff(day,cte.join_date,cte.order_date)<=7 and datediff(day,cte.join_date,cte.order_date)>=0 
      then total_points*2 else total_points+cte.points end total_points 
  from cte2
  inner join cte on cte2.customer_id=cte.customer_id and cte2.rn+1=cte.rn
),last_points_cte as (
  select customer_id,max(order_date) last_day_january,max(rn) max_rn from cte2
  where month(order_date)=1
  group by customer_id
)
select cte2.customer_id,cte2.total_points from cte2
inner join last_points_cte lcte on cte2.customer_id=lcte.customer_id 
                                    and cte2.order_date=lcte.last_day_january
                                    and cte2.rn=lcte.max_rn
```

### <p align='center'>Bonus Questions
#### 1. Join All The Things
The following questions are related creating basic data tables that Danny and his team can use to quickly derive insights without needing to join the underlying tables using SQL.

| customer_id | order_date | product_name | price | member |
|-------------|------------|--------------|-------|--------|
| A           | 2021-01-01 | curry        | 15    | N      |
| A           | 2021-01-01 | sushi        | 10    | N      |
| A           | 2021-01-07 | curry        | 15    | Y      |
| A           | 2021-01-10 | ramen        | 12    | Y      |
| A           | 2021-01-11 | ramen        | 12    | Y      |
| A           | 2021-01-11 | ramen        | 12    | Y      |
| B           | 2021-01-01 | curry        | 15    | N      |
| B           | 2021-01-02 | curry        | 15    | N      |
| B           | 2021-01-04 | sushi        | 10    | N      |
| B           | 2021-01-11 | sushi        | 10    | Y      |
| B           | 2021-01-16 | ramen        | 12    | Y      |
| B           | 2021-02-01 | ramen        | 12    | Y      |
| C           | 2021-01-01 | ramen        | 12    | N      |
| C           | 2021-01-01 | ramen        | 12    | N      |
| C           | 2021-01-07 | ramen        | 12    | N      |

```sql
select s.customer_id,s.order_date,me.product_name,me.price,
  case when s.customer_id in (select customer_id from members) and m.join_date<=s.order_date then 'Y' else 'N' end members from sales s
left join members m on s.customer_id = m.customer_id
inner join menu me on s.product_id = me.product_id
```
#### 2. Rank All The Things
Danny also requires further information about the ranking of customer products, but he purposely does not need the ranking for non-member purchases so he expects null ranking values for the records when customers are not yet part of the loyalty program.
```sql
with cte as (
  select s.customer_id,s.order_date,me.product_name,me.price,
    case when s.customer_id in (select customer_id from members) and m.join_date<=s.order_date then 'Y' else 'N' end members from sales s
  left join members m on s.customer_id = m.customer_id
  inner join menu me on s.product_id = me.product_id
),ranking_cte as (
  select *,rank() over(partition by customer_id order by order_date) rnk from cte
  where members='Y'
  union all
  select *,null rnk from cte
  where members='N'
)
select * from ranking_cte
order by customer_id,order_date
```
