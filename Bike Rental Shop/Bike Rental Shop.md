# <p align="center" style="margin-top: 0px;">Case Study: Bike Rental Shop 
## Notes
- ##### Case study's data and questions were extracted from this link: [here](https://techtfq.com/blog/sql-case-study-bike-rental-shop-practice-sql-queries). 
- ##### All questions were solved using PostgreSQL

## <p align="center">Introduction
Emily is the shop owner, and she would like to gather data to help her grow the
business. She has hired you as an SQL specialist to get the answers to her
business questions such as How many bikes does the shop own by category?
What was the rental revenue for each month? etc. The answers are hidden in the
database. You just need to figure out how to get them out using SQL.

### Understanding the database:
The shop's database consists of 5 tables:

- customer
- bike
- rental
- membership_type
- membership

### The customer table
In the first table, customer , you'll find details about the customers of the bike rental
shop. This table contains the following columns:

	- id : The unique ID of each customer.
	- name : The customer's name.
	- email : The customer's email address.

### The bike table
In the bike table, you'll find information about bikes the rental shop owns.
This table contains the following columns:

	- id : The unique ID of the bike.
	- model : The model of the bike.
	- category : The type of bike (e.g., mountain bike, road bike, hybrid, electric).
	- price_per_hour : The rental price per hour for the bike.
	- price_per_day : The rental price per day for the bike.
	- status : The status of the bike (available, rented, out of service).

### The rental table
The rental table matches customers with bikes they have rented. This table has
the following columns:

	- id : The unique ID of the rental entry.
	- customer_id : The ID of the customer who rented the bike.
	- bike_id : The ID of the bike rented.
	- start_timestamp : The date and time when the rental started.
	- duration : The duration of the rental in minutes.
	- total_paid : The total amount paid for the rental.

### The membership_type table
The membership_type table has information about the different membership types for
purchase. This table contains the following columns:

	- id : The unique ID of the membership type.
	- name : The name of the membership type.
	- description : A description of the membership type.
	- price : The price of the membership type.

### The membership table
The membership table has information about individual memberships purchased by
customers. This table contains the following columns:

	- id : The unique ID of the membership.
	- membership_type_id : The ID of the membership type purchased.
	- customer_id : The ID of the customer who purchased the membership.
	- start_date : The start date of the membership.
	- end_date : The end date of the membership.
	- total_paid : The total amount paid for the membership.

#### You will find the sql scripts to create this dataset in the txt file "data.txt"

## <p align="center">Questions
Following are the business questions that Emily wants answers to. Use SQL to
answer them. All the best.

##### 1. Emily would like to know how many bikes the shop owns by category. Can you get this for her? Display the category name and the number of bikes the shop owns in each category (call this column number_of_bikes ). Show only the categories where the number of bikes is greater than 2 .
```sql
select category,count(distinct model) number_of_bikes from bike
group by category
having count(distinct model)>2
```
#### Output: 

| category       | number_of_bikes |
|----------------|-----------------|
| mountain bike  | 3               |
| road bike      | 3               |

##### 2. Emily needs a list of customer names with the total number of memberships purchased by each. For each customer, display the customer's name and the count of memberships purchased (call this column membership_count ). Sort the results by membership_count , starting with the customer who has purchased the highest number of memberships. Keep in mind that some customers may not have purchased any memberships yet. In such a situation, display 0 for the membership_count .
```sql
select c.name,count(m.id) membership_count from membership m
right join customer c on m.customer_id=c.id
group by c.name
order by 2 desc
```
##### Output:

| name           | membership_count |
|----------------|------------------|
| Alice Smith    | 3                |
| Bob Johnson    | 3                |
| John Doe       | 2                |
| Eva Brown      | 2                |
| Michael Lee    | 2                |
| Daniel Miller  | 0                |
| Sarah White    | 0                |
| Olivia Taylor  | 0                |
| David Wilson   | 0                |
| Emily Davis    | 0                |

##### 3. Emily is working on a special offer for the winter months. Can you help her prepare a list of new rental prices? For each bike, display its ID, category, old price per hour (call this column old_price_per_hour ), discounted price per hour (call it new_price_per_hour ), old price per day (call it old_price_per_day ), and discounted price per day (call it new_price_per_day ). Electric bikes should have a 10% discount for hourly rentals and a 20% discount for daily rentals. Mountain bikes should have a 20% discount for hourly rentals and a 50% discount for daily rentals. All other bikes should have a 50% discount for all types of rentals. Round the new prices to 2 decimal digits.
```sql
select id,category,
	price_per_hour old_price_per_hour, 
	round(case when category='electric' then price_per_hour*0.9
		when category='mountain bike' then price_per_hour*0.8
		else price_per_hour*0.5 end,2) new_price_per_hour,
	price_per_day old_price_per_day,
	round(case when category='electric' then price_per_day*0.8
		else price_per_day*0.5 end,2) new_price_per_day
from bike
```
##### Output:

| id | category       | old_price_per_hour | new_price_per_hour | old_price_per_day | new_price_per_day |
|----|-----------------|--------------------|--------------------|-------------------|-------------------|
| 1  | mountain bike   | 10.00             | 8.00              | 50.00            | 25.00            |
| 2  | road bike       | 12.00             | 6.00              | 60.00            | 30.00            |
| 3  | hybrid          | 8.00              | 4.00              | 40.00            | 20.00            |
| 4  | electric        | 15.00             | 13.50             | 75.00            | 60.00            |
| 5  | mountain bike   | 10.00             | 8.00              | 50.00            | 25.00            |
| 6  | road bike       | 12.00             | 6.00              | 60.00            | 30.00            |
| 7  | hybrid          | 8.00              | 4.00              | 40.00            | 20.00            |
| 8  | electric        | 15.00             | 13.50             | 75.00            | 60.00            |
| 9  | mountain bike   | 10.00             | 8.00              | 50.00            | 25.00            |
| 10 | road bike       | 12.00             | 6.00              | 60.00            | 30.00            |


##### 4. Emily is looking for counts of the rented bikes and of the available bikes in each category. Display the number of available bikes (call this column available_bikes_count ) and the number of rented bikes (call this column rented_bikes_count ) by bike category. 
```sql
select category, sum(case when status='available' then 1 else 0 end) available_bikes_count,
	sum(case when status='rented' then 1 else 0 end) rented_bikes_count from bike
group by category
```
##### Output:

| category       | available_bikes_count | rented_bikes_count |
|----------------|-----------------------|---------------------|
| road bike      | 3                     | 0                  |
| electric       | 2                     | 0                  |
| mountain bike  | 1                     | 1                  |
| hybrid         | 0                     | 1                  |

##### 5. Emily is preparing a sales report. She needs to know the total revenue from rentals by month, the total by year, and the all-time across all the years. Display the total revenue from rentals for each month, the total for each year, and the total across all the years. Do not take memberships into account. There should be 3 columns: year , month , and revenue. Sort the results chronologically. Display the year total after all the month totals for the corresponding year. Show the all-time total as the last row. The resulting table looks something like this:

| year | month | revenue |
|------|-------|---------|
| 2022 | 11    | 200.00  |
| 2022 | 12    | 150.00  |
| 2022 | null  | 350.00  |
| 2023 | 1     | 110.00  |
| ...  | ...   | ...     |
| 2023 | 10    | 335.00  |
| 2023 | null  | 1370.00 |
| null | null  | 1720.00 |

```sql
select extract(year from start_timestamp) "year", extract(month from start_timestamp) "month",
	sum(total_paid) revenue from rental
group by rollup (extract(year from start_timestamp), extract(month from start_timestamp))
order by 1,2
```
##### Output:

| year | month | revenue |
|------|-------|---------|
| 2022 | 11    | 200.00  |
| 2022 | 12    | 150.00  |
| 2022 |       | 350.00  |
| 2023 | 1     | 110.00  |
| 2023 | 2     | 40.00   |
| 2023 | 3     | 110.00  |
| 2023 | 4     | 90.00   |
| 2023 | 5     | 120.00  |
| 2023 | 6     | 115.00  |
| 2023 | 7     | 150.00  |
| 2023 | 8     | 125.00  |
| 2023 | 9     | 175.00  |
| 2023 | 10    | 335.00  |
| 2023 |       | 1370.00 |
|      |       | 1720.00 |

##### 6. Emily has asked you to get the total revenue from memberships for each combination of year, month, and membership type. Display the year, the month, the name of the membership type (call this column membership_type_name ), and the total revenue (call this column total_revenue ) for every combination of year, month, and membership type. Sort the results by year, month, and name of membership type.
```sql
select extract(year from m.start_date) "year", extract(month from m.start_date) "month",
	mt.name membership_type_name,sum(m.total_paid) total_revenue
from membership m
inner join membership_type mt on m.membership_type_id=mt.id
group by rollup (extract(year from m.start_date), extract(month from m.start_date),mt.name)
order by 1,2,3
```
##### Output:

| year | month | membership_type_name | total_revenue |
|------|-------|---------------------- |---------------|
| 2023 | 8     | Basic Annual          | 500.00       |
| 2023 | 8     | Basic Monthly         | 100.00       |
| 2023 | 8     | Premium Monthly       | 200.00       |
| 2023 | 8     |                       | 800.00       |
| 2023 | 9     | Basic Annual          | 500.00       |
| 2023 | 9     | Basic Monthly         | 100.00       |
| 2023 | 9     | Premium Monthly       | 200.00       |
| 2023 | 9     |                       | 800.00       |
| 2023 | 10    | Basic Annual          | 500.00       |
| 2023 | 10    | Basic Monthly         | 100.00       |
| 2023 | 10    | Premium Monthly       | 200.00       |
| 2023 | 10    |                       | 800.00       |
| 2023 | 11    | Basic Annual          | 500.00       |
| 2023 | 11    | Basic Monthly         | 100.00       |
| 2023 | 11    | Premium Monthly       | 200.00       |
| 2023 | 11    |                       | 800.00       |
| 2023 |       |                       | 3200.00      |
|      |       |                       | 3200.00      |

##### 7. Next, Emily would like data about memberships purchased in 2023, with subtotals and grand totals for all the different combinations of membership types and months. Display the total revenue from memberships purchased in 2023 for each combination of month and membership type. Generate subtotals and grand totals for all possible combinations. There should be 3 columns: membership_type_name , month , and total_revenue . Sort the results by membership type name alphabetically and then chronologically by month.
```sql
select mt.name membership_type_name,extract(month from m.start_date) "month",
	sum(m.total_paid) total_revenue
from membership m
inner join membership_type mt on m.membership_type_id=mt.id
group by cube (mt.name,extract(month from m.start_date))
order by 1,2
```
##### Output:

| membership_type_name | month | total_revenue |
|----------------------|-------|---------------|
| Basic Annual         | 8     | 500.00        |
| Basic Annual         | 9     | 500.00        |
| Basic Annual         | 10    | 500.00        |
| Basic Annual         | 11    | 500.00        |
| Basic Annual         |       | 2000.00       |
| Basic Monthly        | 8     | 100.00        |
| Basic Monthly        | 9     | 100.00        |
| Basic Monthly        | 10    | 100.00        |
| Basic Monthly        | 11    | 100.00        |
| Basic Monthly        |       | 400.00        |
| Premium Monthly      | 8     | 200.00        |
| Premium Monthly      | 9     | 200.00        |
| Premium Monthly      | 10    | 200.00        |
| Premium Monthly      | 11    | 200.00        |
| Premium Monthly      |       | 800.00        |
|                      | 8     | 800.00        |
|                      | 9     | 800.00        |
|                      | 10    | 800.00        |
|                      | 11    | 800.00        |
|                      |       | 3200.00       |

##### 8. Now it's time for the final task. Emily wants to segment customers based on the number of rentals and see the count of customers in each segment. Use your SQL skills to get this! Categorize customers based on their rental history as follows: 

	- Customers who have had more than 10 rentals are categorized as 'more than 10'. Customers who have had 5 to 10 rentals (inclusive) are categorized as 'between 5 and 10'. 
	- Customers who have had fewer than 5 rentals should be categorized as 'fewer than 5'.
	- Calculate the number of customers in each category. Display two columns: 
	rental_count_category (the rental count category) and customer_count (the
	number of customers in each category

```sql
with categorized_customer_cte as (
	select c.id,c.name,count(r.id) number_of_rentals,
		case when count(r.id)>10 then 'more than 10'
			when count(r.id)>=5 then 'between 5 and 10'
			else 'fewer than 5' end rental_count_category 
	from rental r
	inner join customer c on r.customer_id=c.id
	group by c.id
)
select rental_count_category,count(id) customer_count from categorized_customer_cte
group by rental_count_category
order by 2 desc
```
##### Output:

| rental_count_category | customer_count |
|-----------------------|----------------|
| fewer than 5          | 8              |
| between 5 and 10      | 1              |
| more than 10          | 1              |