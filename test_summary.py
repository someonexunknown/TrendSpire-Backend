import requests
import json

r = requests.get('http://localhost:5000/api/trends/summary')
d = r.json()
print('Status:', r.status_code)
print('Count:', d['count'])
for x in d['data']:
    print(f"  {x['keyword']:30s} score={x['trend_score']:5.1f}  {x['classification']:15s}  {x['recommendation']}")
