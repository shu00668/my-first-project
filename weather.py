import urllib.request
import urllib.parse
import json
import ssl

ssl._create_default_https_context=ssl._create_unverified_context

API_KEY="CWA-EAC87971-1BAE-4036-8238-130BDF6E1F17"
CITY="桃園市"

url=(
        "https://opendata.cwa.gov.tw/api/v1/rest/datastore/"
        f"F-C0032-001?Authorization={API_KEY}&locationName={urllib.parse.quote(CITY)}"
    )

try:
    with urllib.request.urlopen(url) as response:
        data=json.loads(response.read().decode())
except Exception as e:
    print("API 讀取失敗",e)
    exit()

if"records"not in data or not data["records"]["location"]:
    print("API 資料異常")
    exit()

location=data["records"]["location"][0]
weather_elements=location["weatherElement"]

elements={}

for e in weather_elements:
    elements[e["elementName"]] = e["time"]

wx=elements["Wx"]
pop=elements["PoP"]
temp=elements["MinT"]

def safe_int(x):
    return int(x) if x.isdigit() else 0

daily={}

for i in range(len(wx)):
    date=wx[i]["startTime"][:10]
    weather=wx[i]["parameter"]["parameterName"]

    rain=safe_int(pop[i]["parameter"]["parameterName"])
    t=safe_int(temp[i]["parameter"]["parameterName"])

    if date not in daily:
        daily[date]={
            "rain":[],
            "temp":[],
            "weather":[]
        }

    daily[date]["rain"].append(rain)
    daily[date]["temp"].append(t)
    daily[date]["weather"].append(weather)

rain_days=0
hot_days=0
cold_days=0

for date, d in daily.items():
    avg_rain=sum(d["rain"])/len(d["rain"])
    avg_temp=sum(d["temp"])/len(d["temp"])

    if avg_rain>=60:
        rain_days+=1
    elif avg_temp>=32:
        hot_days+=1
    elif avg_temp<=15:
        cold_days+=1
        
print("\n每 6 小時天氣分析：")

for i in range(len(wx)):
    time=wx[i]["startTime"]
    weather=wx[i]["parameter"]["parameterName"]
    rain=safe_int(pop[i]["parameter"]["parameterName"])
    tempv=safe_int(temp[i]["parameter"]["parameterName"])

    print(f"\n{time}")
    print(f"天氣：{weather}")
    print(f"溫度：{tempv}°C")
    print(f"降雨機率：{rain}%")

    if rain>=60:
        print("建議：帶雨具")
    elif tempv>=32:
        print("建議：注意防曬")
    elif tempv<=15:
        print("建議：注意保暖")
    else:
        print("建議：天氣穩定")

    print("-"*40)

all_temps=[sum(d["temp"])/len(d["temp"])for d in daily.values()]
all_rains=[sum(d["rain"])/len(d["rain"])for d in daily.values()]
avg_temp=sum(all_temps)/len(all_temps)
max_rain=max(all_rains)

print("\n整體天氣分析：")
print(f"平均溫度：{avg_temp:.1f}°C")
print(f"最高降雨機率：{max_rain:.1f}%")
print("\n生活建議：")

if rain_days>=2:
    print("本週多雨，建議攜帶雨具")
if hot_days>=2:
    print("天氣偏熱，注意補水")
if cold_days>=2:
    print("氣溫偏低，注意保暖")
if rain_days==0 and hot_days==0 and cold_days==0:
    print("天氣穩定，適合外出活動")