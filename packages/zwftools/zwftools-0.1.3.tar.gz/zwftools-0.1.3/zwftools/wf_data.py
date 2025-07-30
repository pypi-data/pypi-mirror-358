import pandas as pd

def split_qty( data_base : pd.DataFrame,data_sum:pd.DataFrame,data_base_key,data_sum_key,base_col,split_col,perc = 2):
  # 检查key是否为单字段还是字段数组
 
  unmatched_left  =  unmathched_rows(data_base,data_sum,data_base_key,data_sum_key)
  unmatched_sum  =  unmathched_rows(data_sum,data_base,data_base_key,data_sum_key)
  
  # 合并data_base和data_sum，按key对齐
  merged = pd.merge(
      data_base,
      data_sum[[*([data_sum_key] if isinstance(data_sum_key, str) else data_sum_key), split_col]],
      left_on=data_base_key,
      right_on=data_sum_key,
      how='left',
      suffixes=('', '_sum')
  )
  # 计算每组base_col的总和
  group_keys = [data_base_key] if isinstance(data_base_key, str) else list(data_base_key)
  base_col_sum = merged.groupby(group_keys)[base_col].transform('sum')

  # 计算分配比例
  merged['__ratio'] = merged[base_col] / base_col_sum

  # 分配split_col
  merged[f'split_{split_col}'] = (merged[split_col] * merged['__ratio']).round(perc)
  
  # 将分配结果合并回原data_base
  data_base[f'split_{split_col}'] = merged[f'split_{split_col}']
  # 处理尾差，确保每组分配后的split_col总和与原始split_col总和完全一致
  for keys, group in merged.groupby(group_keys):
    # 获取当前key对应的原始split_col总和（从data_sum中取）
    if isinstance(keys, tuple):
      key_dict = dict(zip(group_keys, keys))
      mask = (data_sum[group_keys] == pd.Series(key_dict)).all(axis=1)
    else:
      mask = data_sum[group_keys[0]] == keys
    original_total = data_sum.loc[mask, split_col].sum()
    assigned_total = group[f'split_{split_col}'].sum()
    diff = round(original_total - assigned_total, perc)
    if abs(diff) >= 10 ** (-perc):
      # 在data_base中找到对应key的行，再找base_col最大的那一行
      if isinstance(keys, tuple):
        base_mask = (data_base[group_keys] == pd.Series(dict(zip(group_keys, keys)))).all(axis=1)
      else:
        base_mask = data_base[group_keys[0]] == keys
      base_group = data_base[base_mask]
      idx = base_group[base_col].idxmax()
      data_base.loc[idx, f'split_{split_col}'] += diff
  
  return {"splited":data_base,"unmatched_left":unmatched_left,"unmatched_right":unmatched_sum}

def unmathched_rows(data_base : pd.DataFrame,data_sum:pd.DataFrame,data_base_key,data_sum_key):
  if isinstance(data_base_key, str):
    base_keys = [data_base_key]
  else:
    base_keys = list(data_base_key)

  if isinstance(data_sum_key, str):
    sum_keys = [data_sum_key]
  else:
    sum_keys = list(data_sum_key)

  # 获取data_sum的key集合
  sum_key_set = set(tuple(row) for row in data_sum[sum_keys].values)

  # 检查data_base中不在data_sum中的行
  mask = ~data_base[base_keys].apply(tuple, axis=1).isin(sum_key_set)
  unmatched_rows = data_base[mask]

  return unmatched_rows
