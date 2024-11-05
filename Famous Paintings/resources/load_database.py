import os
import pandas as pd
from sqlalchemy import create_engine
from decouple import config

conn=config('DATABASE_URL')
db=create_engine(conn)
conn=db.connect()

path=config('DATASET_URL')
files=os.listdir(path)

for file in files:
	if os.path.splitext(file)[1]=='.csv':
		archivo_csv=f'{path}//{file}'
		df=pd.read_csv(archivo_csv)
		table_name=os.path.splitext(file)[0]
		df.to_sql(table_name,conn,index=False,if_exists='replace')
		print(f'Table: {table_name} done')
	else:
		print(f'File: {file} is not a csv file, it is {os.path.splitext(file)[1]}')

conn.close()