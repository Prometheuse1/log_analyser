import requests
from requests import Response

def get_locations(ip):
    response=requests.get("https://ipinfo.io/"+ip+"/json")
    if response.status_code == 200 :
        print(response.json())

if __name__ == '__main__':
    print(get_locations('109.199.110.135'))