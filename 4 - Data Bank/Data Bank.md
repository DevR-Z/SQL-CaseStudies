# <p align="center" style="margin-top: 0px;">Case Study #4: Data Bank
## <p align="center"><img src="" alt="Image" width="400" height="420">

## <p align="center">Notes
- ##### Case study's data and questions were extracted from this link: [here](https://8weeksqlchallenge.com/case-study-4/). 
- ##### All questions were solved using MSSQL Server

## <p align="center">Introduction
Danny thought that there should be some sort of intersection between these new age banks, cryptocurrency and the data world…so he decides to launch a new initiative - Data Bank!
Data Bank runs just like any other digital bank - but it isn’t only for banking activities, they also have the world’s most secure distributed data storage platform!
This case study is all about calculating metrics, growth and helping the business analyse their data in a smart way to better forecast and plan for their future developments!

## <p align="center">Questions
The following case study questions include some general data exploration analysis for the nodes and transactions before diving right into the core business questions and finishes with a challenging final request!

### <p align="center">A. Customer Nodes Exploration
#### 1.How many unique nodes are there on the Data Bank system?
```sql
select count(distinct node_id) nro_nodes from customer_nodes
```
#### 2.What is the number of nodes per region?
```sql
select r.*,count(node_id) nro_nodes from customer_nodes n
inner join regions r on n.region_id=r.region_id
group by r.region_id,r.region_name
order by 1
```
#### 3.How many customers are allocated to each region?
```sql
select r.*,count(distinct customer_id) nro_customers from customer_nodes n
inner join regions r on n.region_id=r.region_id
group by r.region_id,r.region_name
order by 1
```
#### 4.How many days on average are customers reallocated to a different node?
```sql
with cte as (
  select datediff(day,start_date,end_date) days_in_node from customer_nodes
  where year(end_date)=2020
)
select round(avg(days_in_node*1.0),2) avg_in_node from cte
```
#### 5.What is the median, 80th and 95th percentile for this same reallocation days metric for each region?
```sql
with cte as (
  select *,datediff(day,start_date,end_date) days_in_node from customer_nodes
)
select distinct r.region_name,
  percentile_cont(0.5) within group (order by days_in_node) over(partition by r.region_name) median,
  round(percentile_cont(0.8) within group (order by days_in_node) over(partition by r.region_name),2) th80_percentile,
  round(percentile_cont(0.95) within group (order by days_in_node) over(partition by r.region_name),2) th95_percentile
from cte
inner join regions r on cte.region_id=r.region_id
group by r.region_name,days_in_node
```
### <p align="center">B. Customer Transactions
#### 1.What is the unique count and total amount for each transaction type?
```sql
select txn_type,sum(txn_amount) total_amoun from customer_transactions
group by txn_type
order by 2 desc
```
#### 2.What is the average total historical deposit counts and amounts for all customers?
```sql
select customer_id,avg(txn_amount) avg_deposit,sum(txn_amount) total_deposit,count(customer_id) nro_txn from customer_transactions
where txn_type="deposit"
group by customer_id
order by 1
```
#### 3.For each month - how many Data Bank customers make more than 1 deposit and either 1 purchase or 1 withdrawal in a single month?
```sql
with more_1_deposit as (
  select customer_id,count(customer_id) nro_txn from customer_transactions
  where txn_type='deposit'
  group by customer_id
  having count(customer_id)>1
),one_purchase_or_withdrawal as (
  select customer_id,count(customer_id) nro_txn from customer_transactions
  where txn_type='purchase'
  group by customer_id
  having count(customer_id)=1
  union
  select customer_id,count(customer_id) nro_txn from customer_transactions
  where txn_type='withdrawal'
  group by customer_id
  having count(customer_id)=1
)
select customer_id from more_1_deposit
where customer_id in (select distinct customer_id from one_purchase_or_withdrawal)
order by 1
```
#### 4.What is the closing balance for each customer at the end of the month?
```sql
with red_txn as (
  select *,case when txn_type in ('purchase','withdrawal') then txn_amount*-1 else txn_amount end txn 
  from customer_transactions
),balance_acc as (
  select *,sum(txn) over(partition by customer_id order by txn_date) balance_acc
  from red_txn
),balance_end_month as (
  select *,first_value(balance_acc) over(partition by customer_id,month(txn_date) order by txn_date desc range 
                                        between unbounded preceding and unbounded following) last_balance
  from balance_acc
)
select distinct customer_id,month(txn_date) month,last_balance from balance_end_month
```
#### 5.What is the percentage of customers who increase their closing balance by more than 5%?
```sql
with red_txn as (
  select *,case when txn_type in ('purchase','withdrawal') then txn_amount*-1 else txn_amount end txn 
  from customer_transactions
),balance_acc as (
  select *,sum(txn) over(partition by customer_id order by txn_date) balance_acc
  from red_txn
),balance_end_month as (
  select *,first_value(balance_acc) over(partition by customer_id,month(txn_date) order by txn_date desc range 
                                        between unbounded preceding and unbounded following) last_balance
  from balance_acc
),distinct_data as (
  select distinct customer_id,month(txn_date) month,last_balance
  from balance_end_month
),prev_balance as (
  select *,coalesce(lag(last_balance) over(partition by customer_id order by month),0) prev_balance
  from distinct_data
)
select *,case when prev_balance=0 then 0 else round((last_balance-prev_balance)*100.0/prev_balance,2) end growth from prev_balance
```
### <p align="center">C. Data Allocation Challenge
To test out a few different hypotheses - the Data Bank team wants to run an experiment where different groups of customers would be allocated data using 3 different options:

  - Option 1: data is allocated based off the amount of money at the end of the previous month.
  - Option 2: data is allocated on the average amount of money kept in the account in the previous 30 days.
  - Option 3: data is updated real-time.

For this multi-part challenge question - you have been requested to generate the following data elements to help the Data Bank team estimate how much data will need to be provisioned for each option:

  - running customer balance column that includes the impact each transaction
  - customer balance at the end of each month
  - minimum, average and maximum values of the running balance for each customer

#### Using all of the data available - how much data would have been required for each option on a monthly basis?
Running customer balance column that includes the impact each transaction
```sql
select *,sum(case when txn_type in ('purchase','withdrawal') then txn_amount*-1 else txn_amount end) 
          over(partition by customer_id order by txn_date) current_balance
from customer_transactions
where customer_id=1
```
Customer balance at the end of each month
```sql
with red_txn as (
  select *,case when txn_type in ('purchase','withdrawal') then txn_amount*-1 else txn_amount end txn 
  from customer_transactions
),balance_acc as (
  select *,sum(txn) over(partition by customer_id order by txn_date) balance_acc
  from red_txn
),balance_end_month as (
  select *,month(txn_date) month_date,first_value(balance_acc) over(partition by customer_id,month(txn_date) order by txn_date desc range 
                                        between unbounded preceding and unbounded following) last_balance
  from balance_acc
),balance_unique_end_month as (
  select distinct customer_id,month_date,last_balance from balance_end_month
),all_months as (
  select customer_id,month_date,
    coalesce(lead(month_date) over(partition by customer_id order by month_date),12) next_txn_date,last_balance 
  from balance_unique_end_month
  where customer_id in (1,2,3,4,5)
  union all
  select customer_id,month_date+1 month_date,
    next_txn_date,last_balance from all_months
  where month_date+1<next_txn_date
)
select customer_id,month_date,last_balance from all_months
union
select customer_id,next_txn_date month_date,last_balance from all_months
where next_txn_date=12
order by 1,2
```
#### Minimum, average and maximum values of the running balance for each customer
```sql
select customer_id,min(txn_amount) min_txn,avg(txn_amount) avg_txn,max(txn_amount) max_txn from customer_transactions
group by customer_id
order by 1
```
### <p align="center">D. Extra Challenge
Data Bank wants to try another option which is a bit more difficult to implement - they want to calculate data growth using an interest calculation, just like in a traditional savings account you might have with a bank.

If the annual interest rate is set at 6% and the Data Bank team wants to reward its customers by increasing their data allocation based off the interest calculated on a daily basis at the end of each day, how much data would be required for this option on a monthly basis?

#### Special notes:

- Data Bank wants an initial calculation which does not allow for compounding interest, however they may also be interested in a daily compounding interest calculation so you can try to perform this calculation if you have the stamina!
```sql
with cte as (
  select row_number() over(partition by customer_id order by txn_date) rn,
    customer_id,txn_date,
    case when txn_type in ('purchase','withdrawal') then txn_amount*-1 else txn_amount end txn_amount,
    coalesce(lead(txn_date) over(partition by customer_id order by txn_date),'2020-04-30') next_txn_date,
    datediff(day,txn_date,coalesce(lead(txn_date) over(partition by customer_id order by txn_date),'2020-04-30')) days_btw_txn
  from customer_transactions
  where customer_id in (1,10)
),cte2 as (
  select rn,customer_id,txn_date,txn_amount,days_btw_txn,
    case when rn=1 then cast(txn_amount*days_btw_txn*0.005 as decimal(8,3)) else 0.0 end interest_earned,
    case when rn=1 then cast(txn_amount+txn_amount*days_btw_txn*0.005 as decimal(8,3)) else 0.0 end balance_acc
  from cte
),simple_interest as (
  select rn,customer_id,txn_date,txn_amount,days_btw_txn,
    cast(interest_earned as decimal(8,3)) interest_earned,
    cast(balance_acc as decimal(8,3)) balance_acc from cte2
  where rn=1
    union all
  select c2.rn,c2.customer_id,c2.txn_date,c2.txn_amount,c2.days_btw_txn,
    case when c1.balance_acc+c2.txn_amount>0 then cast((c1.balance_acc+c2.txn_amount)*c2.days_btw_txn*0.005 as decimal(8,3)) else 0.0 end interest_earned,
    cast(c1.balance_acc+c2.txn_amount+
        case when c1.balance_acc+c2.txn_amount>0 
            then (c1.balance_acc+c2.txn_amount)*c2.days_btw_txn*0.005 else 0.0 end as decimal(8,3)) balance_acc
  from simple_interest c1
  inner join cte2 c2 on c1.customer_id=c2.customer_id and c1.rn+1=c2.rn
)
select * from simple_interest
order by 2,1
```