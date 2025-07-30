import pandas as pd
import sqlalchemy
from urllib.parse import quote_plus
conn_parm={
  'server':'',
    'port':'',
    'database':'',
    'username':'',
    'password':''    
}

def get_ms_sql_data(view_name,conn_parm):
# 数据库连接信息
  server = conn_parm['server']
  port = conn_parm['port']
  database = conn_parm['database']
  username = conn_parm['username']
  password = conn_parm['password']

  # 视图名称

  # 构建连接字符串
  driver = 'ODBC Driver 18 for SQL Server'
  conn_str = (
      f"mssql+pyodbc:///?odbc_connect="
      + quote_plus(
          f"DRIVER={{{driver}}};"
          f"SERVER={server},{port};"
          f"DATABASE={database};"
          f"UID={username};"
          f"PWD={password};"
          "TrustServerCertificate=yes;"
      )
  )

  # 创建数据库引擎
  engine = sqlalchemy.create_engine(conn_str)

  # 查询视图数据
  sql = f"SELECT * FROM {view_name}"
  df = pd.read_sql(sql, engine)
  return df