import json
import requests
import math

# Define the URL
url = "https://www.trip.com/restapi/soa2/19913/getTripShopList"
url_review = "https://www.trip.com/restapi/soa2/19707/getReviewSearch"

# Define the payload template
payload_template = {"districtId":599,"index":1,"token":"","count":10,"coordinate":{"coordinateType":"wgs84","latitude":0,"longitude":0},"filter":{"themeFilter":{"idList":[]},"zoneFilter":{"idList":[]},"andThemeFilter":{"idList":[]}},"sortType":1,"head":{"locale":"en-US","cver":"3.0","cid":"1710946138005.ca3cAnRrMhA1","syscode":"999","sid":"","extension":[{"name":"locale","value":"en-US"},{"name":"platform","value":"Online"},{"name":"currency","value":"USD"},{"name":"aid","value":""}]}}
review_payload = {"poiId":102343,"locale":"en-US","pageIndex":1,"commentTagId":0,"pageSize":5,"head":{"locale":"en-US","cver":"3.0","cid":"","sid":"","extension":[{"name":"locale","value":"en-US"},{"name":"platform","value":"Online"},{"name":"currency","value":"USD"},{"name":"aid","value":""}]}}

# Initialize an empty list to store the mapped data
mapped_data = []

# Loop 100 times
step_values = [1 + 10 * i for i in range(0, 54)]
for step in step_values:  # Change range to 1, 101 for 100 iterations
    # Assign current page index to the payload
    print(f"start index {step}")
    payload_template["index"] = step

    # Make the POST request with the updated payload
    response = requests.post(url, json=payload_template)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        results = response_json["shopList"]
        districtname = response_json["districtName"]
        
        # print(response_json)

        # Extract relevant data and append to the mapped_data list
        for item in results:
            review_payload["poiId"] = item["poiId"]
            all_review = []
            to_index = math.ceil(item["commentCount"] / 5)
            for j in range(1, 5):
                review_payload["pageIndex"] = j
                response_review = requests.post(url_review, json=review_payload)
                response_review_json = response_review.json()["reviewList"]
            
                reviews = [
                    {
                        "reviewId": review.get("reviewId"),
                        "headImage": review.get("headImage", ""),
                        "username": review.get("username", ""),
                        "createTime": review.get("createTime", ""),
                        "comment": review.get("translateContent", ""),
                        "userRating": review.get("userRating", 0)
                    }
                    for review in response_review_json
                ]
                all_review.extend(reviews)
            
            mapped_item = {
                "id": item["poiId"],
                "code": item["poiId"],
                "name": item["poiEName"],
                "price": item.get("price", 0),
                "type": "shop",
                "districtName": districtname,
                "rating": item["rating"],
                "reviewCount": len(all_review),
                "gglat": item["coordinate"]["latitude"],
                "gglon": item["coordinate"]["longitude"],
                "imageUrl": item["poiImage"],
                "url": item["detailUrl"],
                "tags": [],
                "reviews": all_review
            }
            mapped_data.append(mapped_item)
        print(f"finish index {step}")
            
    else:
        print(f"Request for Page Index {i} failed with status code:", response.status_code)

# Write the mapped data to a file in JSON format
with open("ml_final/shop.json", "w") as outfile:
    json.dump(mapped_data, outfile)

print("Mapped data saved to mapped_data.json")
