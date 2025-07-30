from hana_ml import ConnectionContext
import re
hana_conn_params = {
  'address': '',      # SAP HANA服务器地址
  'port': '',                    # 端口号，默认30015
  'user': '',          # 用户名
  'password': ''       # 密码
}
client = '800'
schemas = 'SAPHANADB'  # 替换为你的SAP HANA数据库模式

def get_hana_connection(hana_conn_params):
     # 替换为你的SAP HANA数据库模式
    # 配置SAP HANA连接参数
    # ConnectionContext accepts fixed schemas and client parameters directly,
    # so no additional configuration is required here.
    conn = ConnectionContext(
    address=hana_conn_params['address'],
    port=hana_conn_params['port'],
    user=hana_conn_params['user'],
    password=hana_conn_params['password'],
    )
    
    
  
    return conn
def hana_tab(table, columns=None, condition=None):
        
    global schemas
    global client
    conn = get_hana_connection()

    
    # 如果未指定列，则查询所有列
    if columns is None:
      select_clause = "*"
    # 如果传入的是列表，则将其转为逗号分隔的字符串
    elif isinstance(columns, list):
      select_clause = ", ".join(columns)
    else:
      select_clause = columns

    # 默认条件 mandt = client
    sql = f"SELECT {select_clause} FROM {schemas}.{table} where mandt = {client}"
    
    # 如果额外的查询条件非空，则附加到原有条件后
    if condition and isinstance(condition, dict):
      cond_str = " AND ".join(
        f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
        for k, v in condition.items()
      )
      sql += f" and {cond_str}"
    elif condition:
      sql += f" and {condition}"
    df = conn.sql(sql).collect()
    conn.close()
    
    return df
  
def hana_sql(sql):
    conn = get_hana_connection()
    def add_schema(match):
      keyword = match.group(1)
      table = match.group(2)
      if '.' not in table:
        return f"{keyword} {schemas}.{table}"
      return match.group(0)

    sql = re.sub(r"(FROM|JOIN)\s+([^\s;]+)", add_schema, sql, flags=re.IGNORECASE)
    
    # add WHERE condition for the first table
    m = re.search(r"(?i)FROM\s+(\S+)", sql)
    if m:
      first_table = m.group(1)
      if re.search(r"(?i)\bWHERE\b", sql):
        # prepend the condition into the existing WHERE clause
        sql = re.sub(r"(?i)(WHERE\s+)", r"\1" + f"{first_table}.mandt = {client} AND ", sql, count=1)
      else:
        sql += f" WHERE {first_table}.mandt = {client}"

    # add ON condition for each JOIN clause
    def add_on_cond(match):
      table = match.group(2)
      return f"{match.group(1)}{table}.mandt = {client} AND "

    sql = re.sub(r"(?i)(JOIN\s+(\S+)\s+ON\s+)", add_on_cond, sql)
    df = conn.sql(sql).collect()
    conn.close()
    return df
  
  