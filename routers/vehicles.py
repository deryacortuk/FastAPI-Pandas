from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel,json
from api.settings import  base_url
import pandas as pd
import requests
import json
from typing import List, Optional
from routers.users import user_login
import datetime



vehicle_router = APIRouter(tags=["Vehicle"])

@vehicle_router.get("/labels/{labelId}")
def get_color(labelId):
    url = f'{base_url}/dev/index.php/v1/labels/{labelId}'
    access_token = user_login()
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"}  
    response = requests.request("GET",url, headers=headers)
    return response.json()

@vehicle_router.get("/filter/hu")
def filter():
    with open("response.json","r",encoding="utf-8") as file:
        data = json.load(file)        
        filtered_data = [x for x in data if x["hu"] != None]
        
    with open("filter_hu.json", "w") as write_file:
        json.dump(filtered_data, write_file, indent=4)  
    return filtered_data

@vehicle_router.get("/hu")
def check_hu(datas):           
    strToday = datetime.datetime.today().strftime('%Y-%m-%d')
    dateToday = datetime.datetime.strptime(strToday, '%Y-%m-%d')
    for data in datas:
        if data["hu"] and data["colored"]:
            hu = datetime.datetime.strptime(data["hu"], "%Y-%m-%d")
            result = (dateToday.year - hu.year) * 12 + (dateToday.month - hu.month)
            if result < 3:
                data["colorCode"] = "#007500"
            elif result < 12:
                data["colorCode"] = "#FFA500"
            else:
                 data["colorCode"] = "#b30000"                         
                
    return datas



@vehicle_router.post("/upload")
def upload(kys:List[str],url, colored:Optional[bool] = True):
                   
    csvDataFrame = pd.read_csv(url,  encoding='utf8',sep=';',header=None,names=kys)      
       
    df = pd.DataFrame(csvDataFrame)   
    df["colored"] = colored
    datas = df.to_json(orient="table",indent=4)
    
    check_hu(datas)
    
    
    current_date = datetime.datetime.now().isoformat('-',"hours")
    
    with pd.ExcelWriter(f"vehicles_{current_date}.xlsx") as writer:
        datas.to_excel(writer)        
    
    dataframe = pd.read_excel(f"vehicles_{current_date}.xlsx")    
       
    dataframe.to_json('vehicle.json', index=False, orient="table", indent=4)      
       
    
    new_data = datas["data"]            
    return new_data
    
@vehicle_router.post("/vehicle")
def post_data():
    url = f"{base_url}/dev/index.php/v1/vehicles/select/active"    
    access_token = user_login()
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"}  
    
    response = requests.request("GET",url,headers= headers)   
        
    data = json.load(open('vehicle.json'))
    new_data = data["data"]
 
    with open("sorted_vehicle.json", "w", encoding="utf-8") as file1:
        json.dump(sorted(new_data, key=lambda x: (x["gruppe"] is None, x["gruppe"])), file1 ,indent=4)
        
    with open("response.json", "w",encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4)         
   
    return response.json()

@vehicle_router.get("/search")
def search_field(key):
    search_data = []
    with open("reesponse.json","r",encoding="utf-8") as file:
        data = json.load(file)    
        s_data = {}
        for src in data:
            if src[key]:               
                
                s_data[key] = src[key]
                s_data["kurzname"] = src["kurzname"]
                s_data["info"] = src["info"]
                search_data.append(s_data)
                
            else:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Data does not exist.")
                    
        
    return search_data
@vehicle_router.post("/merge")
def merge_data(url1, url2)->dict:
    csvData1 = pd.read_csv(url1,  encoding='utf8',sep=';',error_bad_lines=False)     
    csvData2 = pd.read_csv(url2,  encoding='utf8',sep=';',error_bad_lines=False)  
       
    df1 = pd.DataFrame(csvData1)   
    df2 = pd.DataFrame(csvData2)   
    merge_data = pd.concat([df1,df2]).drop_duplicates().reset_index(drop=True)
    
    merge_data.to_json("merged_data.json", indent=4)
    return merge_data
    
    
    
