import requests

def get_google_img(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "searchType": "image"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "items" in data and len(data["items"]) > 0:
        img_url = data["items"][0]["link"]
        return img_url

    return None

# Set your API key and CX (Custom Search Engine ID) here
api_key = "AIzaSyBtuoL2-dL71kSmh6sPsrLSSpgn1thUYJg"
cx = "15d5cf5fb6e3c484c"

img = get_google_img("Wanted Dead or Alive Bon Jovie", api_key, cx)
print(img)