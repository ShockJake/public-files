from bs4 import BeautifulSoup
import requests
import json

def get_page_data(url : str, session : requests.Session):
    print("[NETWORKING] Sending request to: " + url)
    response = session.get(url, allow_redirects=True)
    
    if response.status_code != 200:
        print("[NETWORING] Bad response: " + str(response.status_code))
    else:
        print("[NETWORKING] Response is ok!")
        
    return response.text


def map_room_number(roomNumber: str):
    if roomNumber == "ONE":
        return 1
    if roomNumber == "TWO":
        return 2
    if roomNumber == "THREE":
        return 3
    if roomNumber == "FOUR":
        return 4
    if roomNumber == "FIVE":
        return 5


def get_json(text : str):
    soup = BeautifulSoup(text, 'html.parser')
    data: BeautifulSoup.tagStack = soup.find(id = '__NEXT_DATA__')
    return  json.loads(data.text)

    
def find_location(location_nodes, title: str):
    for node in location_nodes:
        if node["title"] == title:
            location: str = node["locationLabel"]["value"]
            return location.split(',')[1].strip()
    

def write_data_from_item(item, file, location_nodes):
    null_title = "https://www.otodom.pl/pl/oferta/"
    
    
    if location_nodes != None:  
        title = item["name"]
        url = item["url"]
        rooms = item["itemOffered"]["numberOfRooms"]
        price = item["price"]
        area = item["itemOffered"]["floorSize"]["value"]
        loc = find_location(location_nodes, title)
    else:
        title = item["title"]
        url = null_title + str(item["id"])
        rooms = map_room_number(item["roomsNumber"])
        if item["totalPrice"] != None:
            price = item["totalPrice"]["value"]
        else:
            price = "Null"
        area = item["areaInSquareMeters"]
        loc = item["locationLabel"]["value"].split(',')[1].strip()
    
    # print(f"[I/O] Writing data: {url};{title};{rooms};{price};{area};{loc}")
    file.write(f"{url};{title};{rooms};{price};{area};{loc}\n")    


def parse_data(src: str, file):
    data = get_json(src)
    
    nodes_with_location = data["props"]["pageProps"]["data"]["searchAds"]["items"]
    nodes = data["props"]["pageProps"]["schemaMarkupData"]
    
    if nodes != None:
        nodes = nodes["@graph"][2]["offers"]["offers"]           
        for node in nodes:
            write_data_from_item(node, file, nodes_with_location)
    else:
        for node in nodes_with_location:
            write_data_from_item(node, file, None)
        

def main():
    file = open("data.csv", "a")
    session = requests.Session()
    
    try:
        file.write("url;title;rooms;price;area;loc\n")
        
        url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/krakow?limit=72&page="
        for i in range(1, 20):
            page = get_page_data(url + str(i), session)
            print("Page #" + str(i))
            parse_data(page, file)
    except Exception as e:
        print(e)
    finally:
        session.close()
        file.close()

if __name__ == '__main__':
    main()
