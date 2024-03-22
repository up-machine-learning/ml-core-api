import json
import requests

# Define the URL
url = "https://www.trip.com/restapi/soa2/18361/foodListSearch"
url_review = "https://www.trip.com/restapi/soa2/19707/getReviewSearch"

# Define the payload template
payload_template = {"head":{"cid":"1710946138005.ca3cAnRrMhA1","extension":[{"name":"locale","value":"en-US"},{"name":"platform","value":"Online"},{"name":"currency","value":"USD"}]},"districtId":1524545,"sortType":"score","pageIndex":2,"pageSize":9,"lat":0,"lon":0,"tag":0,"filterType":2,"minPrice":0,"fromPage":""}
review_payload = {"poiId":17772586,"locale":"en-US","pageIndex":0,"commentTagId":0,"pageSize":40,"head":{"cver":"3.0","cid":"","locale":"en-US","extension":[{"name":"locale","value":"en-US"},{"name":"platform","value":"Online"},{"name":"currency","value":"USD"}]}}

# Initialize an empty list to store the mapped data
mapped_data = []

# Loop 100 times
for i in range(1, 100):  # Change range to 1, 101 for 100 iterations
    # Assign current page index to the payload
    print(f"start index {i}")
    payload_template["pageIndex"] = i

    # Make the POST request with the updated payload
    response = requests.post(url, json=payload_template)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        results = response_json["results"]
        districtname = response_json["districtname"]
        
        # print(response_json)

        # Extract relevant data and append to the mapped_data list
        for item in results:
            review_payload["poiId"] = item["poiId"]
            
            all_review = []
            for j in range(1, math.ceil(item["commentCount"] / 5)):
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
                "code": item["restaurantId"],
                "name": item["englishName"],
                "price": item.get("price", 0),
                "type": "restaurant",
                "districtName": districtname,
                "rating": item["rating"],
                "reviewCount": item["reviewCount"],
                "gglat": item["gglat"],
                "gglon": item["gglon"],
                "imageUrl": item["coverImgaeUrl"],
                "url": item["jumpUrl"],
                "tags": [tag_item["tagName"] for tag_item in item["tags"]],
                "reviews": all_review
            }
            mapped_data.append(mapped_item)
        print(f"finish index {i}")
            
    else:
        print(f"Request for Page Index {i} failed with status code:", response.status_code)

# Write the mapped data to a file in JSON format
with open("ml_final/restaurants.json", "w") as outfile:
    json.dump(mapped_data, outfile)

print("Mapped data saved to mapped_data.json")
