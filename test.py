from db import execute_query

data = execute_query("SELECT COUNT(*) FROM public.store_scores;")
print(data)
