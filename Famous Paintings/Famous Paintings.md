# <p align="center" style="margin-top: 0px;">Case Study: Famous Paitings 
## Notes
- ##### Case study's questions were extracted from this link: [here](https://techtfq.com/blog/sql-project-sql-case-study-to-solve-and-practice-sql-queries).
- ##### Case study's dataset were extracted from kaggle: [here](https://www.kaggle.com/datasets/mexwell/famous-paintings)
- ##### All questions were solved using PostgreSQL

## Load dataset
### Method 1 (Manually):
The dataset is available in url to download and import manually in your favorite RDBMS

### Method 2 (Using Python):
The dataset can be loaded automatically using python:

#### Steps:

**1. Download the repository** and save it in a root directory

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate virtual environment**

```bash
venv\scripts\activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Set environment variables**

Create a *.env* file in root directory of your project and add environments variables

- DATABASE_URL=postgresql://db_username:db_password@db_host:db_port/db_name
- path=your_path

Make sure that the .csv files you want to load to the database are in that path

**6. Execute load_database.py**

## Questions

#### 1) Fetch all the paintings which are not displayed on any museums?
```sql
select work_id,name from work where museum_id is null
```

#### 2) Are there museuems without any paintings?
```sql
select m.museum_id,count(w.work_id) nro_paintings from museum m
left join work w on m.museum_id=w.museum_id
group by m.museum_id
having count(w.work_id)=0
```

#### 3) How many paintings have an asking price of more than their regular price? 
```sql
select count(*) from product_size where sale_price>regular_price
```

#### 4) Identify the paintings whose asking price is less than 50% of its regular price
```sql
select * from product_size where sale_price<regular_price*0.5
```

#### 5) Which canva size costs the most?
```sql
select p.size_id,c.label as canva,max(p.sale_price) most_expensive from product_size p
inner join canvas_size c on p.size_id = c.size_id::text
group by p.size_id,c.label
order by 3 desc limit 1
```
##### Output:

| size_id | canva                    | most_expensive |
|---------|---------------------------|----------------|
| 4896    | 48" x 96"(122 cm x 244 cm) | 1115          |

#### 6) Delete duplicate records from work, product_size, subject and image_link tables
##### Solution 1:
```sql
delete from work 
where ctid not in (select min(ctid)
					from work
					group by work_id );
delete from product_size 
where ctid not in (select min(ctid)
					from product_size
					group by work_id, size_id );
delete from subject 
where ctid not in (select min(ctid)
					from subject
					group by work_id, subject );
delete from image_link 
where ctid not in (select min(ctid)
					from image_link
					group by work_id );
```
##### Solution 2:
```sql

with duplicate_work as (
	select *,row_number() over(partition by work_id) as rn from work
)
select work_id,name,artist_id,style,museum_id into work_temp from duplicate_work where rn=1;
truncate table work;
insert into work select * from work_temp;
drop table work_temp;

with duplicate_product_size as (
	select *,row_number() over(partition by work_id,size_id) as rn from product_size
)
select work_id,size_id,sale_price,regular_price into product_size_temp from duplicate_product_size where rn=1;
truncate table product_size;
insert into product_size select * from product_size_temp;
drop table product_size_temp;

with duplicate_subject as (
	select *,row_number() over(partition by work_id,subject) as rn from subject
)
select work_id,subject into subject_temp from duplicate_subject where rn=1;
truncate table subject;
insert into subject select * from subject_temp;
drop table subject_temp;

with duplicate_image_link as (
	select *,row_number() over(partition by work_id) as rn from image_link
)
select work_id,url,thumbnail_small_url,thumbnail_large_url into image_link_temp from duplicate_image_link where rn=1;
truncate table image_link;
insert into image_link select * from image_link_temp;
drop table image_link_temp;
```

#### 7) Identify the museums with invalid city information in the given dataset
```sql
select name,city from museum where city ~ '^[0-9]'
```
##### Output:

|              name               |      city       |
|---------------------------------|-----------------|
| The State Hermitage Museum      | 2               |
| Museum Folkwang                 | 45128           |
| Museum of Grenoble              | 38000           |
| Musée des Beaux-Arts de Quimper | 29000           |
| Musée du Louvre                 | 75001           |
| Kröller-Müller Museum           | 6731 AW Otterlo |

#### 8) Museum_Hours table has 1 invalid entry. Identify it and remove it.
```sql
with duplicate_museum_hours as (
	select *,row_number() over(partition by museum_id,day) rn from museum_hours
)
select * into museum_hours_temp from duplicate_museum_hours where rn=1;
truncate table museum_hours;
insert into museum_hours select museum_id,day,open,close from museum_hours_temp;
drop table museum_hours_temp;
```

#### 9) Fetch the top 10 most famous painting subject
```sql
select s.subject,count(w.work_id) nro_paintings from work w
inner join subject s on w.work_id=s.work_id
where museum_id is not null
group by s.subject
order by 2 desc limit 10
```
##### Output:

|       subject       | nro_paintings |
|---------------------|---------------|
| Portraits           | 510           |
| Marine Art/Maritime | 188           |
| Still-Life          | 161           |
| Nude                | 146           |
| Rivers/Lakes        | 139           |
| Landscape Art       | 118           |
| Christianity        | 116           |
| Flowers             | 111           |
| Seascapes           | 88            |
| Architectures       | 78            |

#### 10) Identify the museums which are open on both Sunday and Monday. Display museum name, city.
##### Solution 1:
```sql
select m.name,m.city from museum_hours mh
inner join museum m on mh.museum_id=m.museum_id
where day='Sunday' and exists (select 1 from museum_hours mh2
								where mh.museum_id=mh2.museum_id and mh2.day='Monday')
order by 1;
```
##### Solution 2:
```sql
with sunday_open_museum as (
	select museum_id from museum_hours where day = 'Sunday'
)
select m.name,m.city from museum_hours mh 
inner join museum m on mh.museum_id = m.museum_id
where mh.day = 'Monday' and mh.museum_id in (select * from sunday_open_museum)
order by 1
```

#### 11) How many museums are open every single day?
```sql
select count(*) nro_museums_every_day from (
	select museum_id,count(distinct day) from museum_hours
	group by museum_id
	having count(distinct day)=7
) x
```
##### Output:

| nro_museums_every_day |
|-----------------------|
| 17                    |

#### 12) Which are the top 5 most popular museum? (Popularity is defined based on most no of paintings in a museum)
```sql
select m.name,count(w.work_id) nro_paintings from work w
inner join museum m on w.museum_id=m.museum_id
where w.museum_id is not null
group by m.name
order by 2 desc limit 5
```
##### Output:

|       subject       | nro_paintings |
|---------------------|---------------|
| Portraits           | 510           |
| Marine Art/Maritime | 188           |
| Still-Life          | 161           |
| Nude                | 146           |
| Rivers/Lakes        | 139           |
| Landscape Art       | 118           |
| Christianity        | 116           |
| Flowers             | 111           |
| Seascapes           | 88            |
| Architectures       | 78            |

#### 13) Who are the top 5 most popular artist? (Popularity is defined based on most no of paintings done by an artist)
```sql
select a.full_name,count(work_id) nro_paintings from work w
inner join artist a on w.artist_id=a.artist_id
where w.artist_id is not null
group by a.full_name
order by 2 desc limit 5
```
##### Output:

|       full_name       | nro_paintings |
|-----------------------|---------------|
| Pierre-Auguste Renoir | 469           |
| Claude Monet          | 378           |
| Vincent Van Gogh      | 308           |
| Maurice Utrillo       | 253           |
| Albert Marquet        | 233           |

#### 14) Display the 3 least popular canva sizes
```sql
with cte as (
	select c.label,count(w.work_id) nro_paintings,dense_rank() over(order by count(w.work_id)) drnk from product_size p
	inner join work w on p.work_id=w.work_id
	inner join canvas_size c on p.size_id = c.size_id::text
	where w.museum_id is not null
	group by c.label
)
select * from cte where drnk<=3
```
##### Output:

|           label           | nro_paintings | drnk |
|---------------------------|---------------|------|
| 45" x 32"(114 cm x 81 cm) | 1             | 1    |
| 37" x 30"(94 cm x 76 cm)  | 1             | 1    |
| 32" x 32"(81 cm x 81 cm)  | 1             | 1    |
| 44" x 34"(112 cm x 86 cm) | 1             | 1    |
| 36" x 27"(91 cm x 69 cm)  | 1             | 1    |
| 32" x 18"(81 cm x 46 cm)  | 1             | 1    |
| 24" x 29"(61 cm x 74 cm)  | 1             | 1    |
| 16" x 32"(41 cm x 81 cm)  | 8             | 2    |
| 20" x 40"(51 cm x 102 cm) | 10            | 3    |

#### 15) Which museum is open for the longest during a day. Dispay museum name, state and hours open and which day?
```sql
with cte as (
	select *,to_timestamp(close,'HH:MI PM')-to_timestamp(open,'HH:MI AM') duration,
		rank() over(order by to_timestamp(close,'HH:MI PM')-to_timestamp(open,'HH:MI AM') desc) rnk
	from museum_hours
)
select m.name,m.state,cte.duration,cte.day from cte
inner join museum m on cte.museum_id=m.museum_id
where rnk=1
```
##### Output:

|       name       |  state | duration |   day   |
|------------------|--------|----------|---------|
| Musée du Louvre  | Paris  | 12:45:00 | Friday  |

#### 16) Which museum has the most no of most popular painting style?
```sql
with cte as (
	select m.name,w.style,count(w.work_id) nro_paintings,
		rank() over(order by count(w.work_id) desc) rnk
	from work w
	inner join museum m on w.museum_id=m.museum_id
	where w.museum_id is not null and w.style is not null
	group by m.name,w.style
)
select name,style,nro_paintings from cte where rnk=1;
```
##### Output:

|              name              |     style     | nro_paintings |
|--------------------------------|---------------|---------------|
| The Metropolitan Museum of Art | Impressionism |           244 |

#### 17) Identify the artists whose paintings are displayed in multiple countries
```sql
select a.full_name,count(distinct m.country) nro_countries from work w
inner join museum m on w.museum_id=m.museum_id
inner join artist a on w.artist_id=a.artist_id
group by a.full_name
having count(distinct m.country)>1
order by 2 desc;
```

#### 18) Display the country and the city with most no of museums. Output 2 seperate columns to mention the city and country. If there are multiple value, seperate them with comma.
```sql
with country_cte as (
	select country,count(museum_id) nro_museums,
		rank() over(order by count(museum_id) desc) rnk
	from museum
	group by country
),city_cte as (
	select city,count(museum_id) nro_museums,
		rank() over(order by count(museum_id) desc) rnk
	from museum
	group by city
)
select (select string_agg(country,',') from country_cte where rnk=1) country,
	(select string_agg(city,',') from city_cte where rnk=1) city
```
##### Output:

| country |               city                |
|---------|----------------------------------|
| USA     | London, Washington, New York, Paris |

#### 19) Identify the artist and the museum where the most expensive and least expensive painting is placed. Display the artist name, sale_price, painting name, museum name, museum city and canvas label
```sql
select a.full_name artist_name,p.sale_price,w.name painting_name,m.name museum_name,m.city,c.label from work w
inner join product_size p on w.work_id=p.work_id
inner join artist a on w.artist_id=a.artist_id
inner join canvas_size c on p.size_id=c.size_id::text
inner join museum m on w.museum_id=m.museum_id
where sale_price=(select max(sale_price) from product_size) or sale_price=(select min(sale_price) from product_size);
```
##### Output:

|       artist_name       | sale_price |                  painting_name                   |          museum_name           |   city   |           label            |
|-------------------------|------------|--------------------------------------------------|--------------------------------|----------|----------------------------|
| Peter Paul Rubens       |       1115 | Fortuna                                          | The Prado Museum               | Madrid   | 48" x 96"(122 cm x 244 cm) |
| Adélaïde Labille-Guiard |         10 | Portrait of Madame Labille-Guyard and Her Pupils | The Metropolitan Museum of Art | New York | 30" Long Edge             |
| Adélaïde Labille-Guiard |         10 | Portrait of Madame Labille-Guyard and Her Pupils | The Metropolitan Museum of Art | New York | 36" Long Edge             |

#### 20) Which country has the 5th highest no of paintings?
```sql
with cte as (
	select m.country,count(w.work_id) nro_paintings,
		dense_rank() over(order by count(w.work_id) desc) drnk
	from work w
	inner join museum m on w.museum_id=m.museum_id
	group by m.country
)
select * from cte where drnk=5
```
##### Output:

| country | nro_paintings | drnk |
|---------|---------------|------|
| Spain   |           196 |    5 |

#### 21) Which are the 3 most popular and 3 least popular painting styles?
```sql
with most_and_least_cte as (
	select style,count(work_id) nro_paintings,
		dense_rank() over(order by count(work_id) desc) m_drnk,
		dense_rank() over(order by count(work_id)) l_drnk
	from work where museum_id is not null and style is not null
	group by style
)
select (select string_agg(concat(style,'(',nro_paintings,')'),',' order by nro_paintings desc) from most_and_least_cte where m_drnk<=3) most_popular,
	(select string_agg(concat(style,'(',nro_paintings,')'),',') from most_and_least_cte where l_drnk<=3) least_popular
```
##### Output:

|                       most_popular                       |                 least_popular                  |
|----------------------------------------------------------|-----------------------------------------------|
| Impressionism(1173), Baroque(643), Post-Impressionism(259) | Japanese Art(1), Art Nouveau(7), Surrealism(13) |

#### 22) Which artist has the most no of Portraits paintings outside USA?. Display artist name, no of paintings and the artist nationality.
```sql
with cte as (
	select a.full_name,a.nationality,count(w.work_id) nro_paintings,
		rank() over(order by count(w.work_id) desc) rnk
	from work w
	inner join artist a on w.artist_id=a.artist_id
	inner join museum m on w.museum_id=m.museum_id
	inner join subject s on w.work_id=s.work_id
	where s.subject='Portraits' and m.country!='USA'
	group by a.full_name,a.nationality
)
select full_name,nationality,nro_paintings from cte where rnk=1;
```
##### Output:

|      full_name      | nationality | nro_paintings |
|---------------------|-------------|---------------|
| Vincent Van Gogh    | Dutch       |            14 |
| Jan Willem Pieneman | Dutch       |            14 |