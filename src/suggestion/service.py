import os
import re

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from math import radians, sin, cos, sqrt, atan2
import json
import joblib
import urllib.parse
from scipy.sparse import hstack

from src.suggestion.schemas import CreateSuggestionDto, CreateResponseDto, DestinationDto, ReviewDto, \
    DestinationPageDto, DestinationResultDto
from src.user.model import User

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_dir = os.path.join(project_dir, 'dataset')
sentiment_model_file = os.path.join(project_dir, 'src/ai_model/sentiment_model.joblib')
vectorizer_model_file = os.path.join(project_dir, 'src/ai_model/vectorizer.joblib')
restaurants_json_path = os.path.join(dataset_dir, 'restaurants.json')
shops_json_path = os.path.join(dataset_dir, 'shops.json')


# Function to calculate haversine distance
def haversine_distance(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    # Compute differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Calculate Haversine distance
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


async def load_dataset():
    # Load data from JSON file
    with open(restaurants_json_path, 'r') as file:
        data_restaurant = json.load(file)

    with open(shops_json_path, 'r') as file:
        data_shop = json.load(file)

    # Convert data to DataFrame
    restaurants_df = pd.DataFrame(data_restaurant)
    shops_df = pd.DataFrame(data_shop)

    combined_df = pd.concat([restaurants_df, shops_df], ignore_index=True)

    # Filter out rows with empty sentiment scores
    combined_df.dropna(subset=['name'], inplace=True)
    combined_df = combined_df[combined_df['name'].str.strip() != '']
    return combined_df


async def build_ai_trip_model():
    # Load data from JSON file
    combined_df = await load_dataset()

    # Calculate sentiment scores for reviews
    sid = SentimentIntensityAnalyzer()
    combined_df['sentiment_scores'] = combined_df['reviews'].apply(
        lambda reviews: [sid.polarity_scores(review['comment'])['compound'] for review in reviews]
    )

    combined_df = combined_df[combined_df['sentiment_scores'].apply(lambda x: len(x) > 0)]
    combined_df['avg_sentiment'] = combined_df['sentiment_scores'].apply(lambda scores: sum(scores) / len(scores))

    print('start training model sentiment')
    vectorizer = TfidfVectorizer()
    X_text = vectorizer.fit_transform(
        combined_df['reviews'].apply(lambda reviews: ' '.join([review['comment'] for review in reviews])))
    y_sentiment = combined_df['avg_sentiment']
    sentiment_model = RandomForestRegressor()

    combined_df['num_reviews'] = combined_df['reviews'].apply(len)
    X_num_reviews = combined_df['num_reviews'].values.reshape(-1, 1)
    X_combined = hstack([X_text, X_num_reviews])

    sentiment_model.fit(X_combined, y_sentiment)
    joblib.dump(sentiment_model, sentiment_model_file)
    joblib.dump(vectorizer, vectorizer_model_file)  # Save the trained vectorizer
    print('finish training model sentiment')
    return 'OK'


async def trip_suggestion(create_dto: CreateSuggestionDto, current_user: User):
    combined_df = await load_dataset()
    # Calculate sentiment scores for reviews
    sid = SentimentIntensityAnalyzer()
    combined_df['sentiment_scores'] = combined_df['reviews'].apply(
        lambda reviews: [sid.polarity_scores(review['comment'])['compound'] for review in reviews]
    )

    combined_df = combined_df[combined_df['sentiment_scores'].apply(lambda x: len(x) > 0)]
    combined_df['avg_sentiment'] = combined_df['sentiment_scores'].apply(lambda scores: sum(scores) / len(scores))

    sentiment_model = joblib.load(sentiment_model_file)
    vectorizer = joblib.load(vectorizer_model_file)

    user_location = (create_dto.latitude, create_dto.longitude)
    desired_tags = create_dto.preferences
    shop_suggestion_one, shop_suggestion_two, shop_suggestion_three = await get_suggestion_by_type(user_location,
                                                                                                   desired_tags,
                                                                                                   "shop", combined_df,
                                                                                                   vectorizer,
                                                                                                   sentiment_model)

    restaurant_suggestion_one, restaurant_suggestion_two, restaurant_suggestion_three = await get_suggestion_by_type(
        user_location,
        desired_tags,
        "restaurant",
        combined_df,
        vectorizer,
        sentiment_model)

    suggestion_one = restaurant_suggestion_one + shop_suggestion_one
    suggestion_two = restaurant_suggestion_two + shop_suggestion_two
    suggestion_three = restaurant_suggestion_three + shop_suggestion_three

    data = CreateResponseDto(optionOne=suggestion_one, optionTwo=suggestion_two, optionThree=suggestion_three)

    return data


async def get_suggestion_by_type(user_location, desired_tags, destination_type, combined_df, vectorizer,
                                 sentiment_model):
    shops_df = combined_df[combined_df['type'] == destination_type].copy()
    shops_df['num_reviews'] = combined_df['reviews'].apply(len)
    X_text = vectorizer.transform(
        shops_df['reviews'].apply(lambda reviews: ' '.join([review['comment'] for review in reviews])))
    X_num_reviews = shops_df['num_reviews'].values.reshape(-1, 1)
    X_combined_test = hstack([X_text, X_num_reviews])
    shops_df['predicted_sentiment'] = sentiment_model.predict(X_combined_test)

    if desired_tags:
        filtered_shops_df = shops_df[shops_df['tags'].apply(lambda tags: any(tag in tags for tag in desired_tags))]
    else:
        filtered_shops_df = shops_df

    # Calculate distances from user's location for filtered shops
    filtered_shops_df['distance'] = filtered_shops_df.apply(
        lambda row: haversine_distance(user_location, (row['gglat'], row['gglon'])), axis=1)

    # Top 5 recommended shops
    top_5_shop_recommendations = filtered_shops_df.sort_values(by=['distance', 'num_reviews', 'avg_sentiment'], ascending=[True, False, False]).head(9)
    # print(top_5_shop_recommendations[
    #           ['id', 'type', 'name', 'avg_sentiment', 'distance', 'predicted_sentiment', 'gglat', 'gglon', 'tags']])
    top_5_shop_recommendation_array = top_5_shop_recommendations.to_numpy()

    shop_option_1 = top_5_shop_recommendation_array[:3, 0]
    shop_option_1_list = filtered_shops_df[filtered_shops_df['id'].isin(shop_option_1)]

    shop_option_2 = top_5_shop_recommendation_array[3:6, 0]
    shop_option_2_list = filtered_shops_df[filtered_shops_df['id'].isin(shop_option_2)]

    shop_option_3 = top_5_shop_recommendation_array[6:9, 0]
    shop_option_3_list = filtered_shops_df[filtered_shops_df['id'].isin(shop_option_3)]

    suggestion_one = await get_map_list_suggestion(shop_option_1_list)
    suggestion_two = await get_map_list_suggestion(shop_option_2_list)
    suggestion_three = await get_map_list_suggestion(shop_option_3_list)
    return suggestion_one, suggestion_two, suggestion_three


async def get_map_list_suggestion(data):
    suggestion_result = []
    for _, row in data.iterrows():
        reviews_with_scores = []
        for idx, review in enumerate(row['reviews']):
            user_rating = row['sentiment_scores'][idx]  # Get sentiment score at the corresponding index
            review_with_score = review.copy()  # Create a copy of the review dictionary
            review_with_score['predictedSentiment'] = user_rating  # Assign sentiment score to userRating
            reviews_with_scores.append(review_with_score)
        destination_dto = DestinationResultDto(
            id=row['id'],
            code=row['code'],
            name=row['name'],
            price=row['price'],
            type=row['type'],
            districtName=row['districtName'],
            rating=row['rating'],
            reviewCount=len(row.get('reviews', 0)),
            gglat=row['gglat'],
            gglon=row['gglon'],
            imageUrl=row['imageUrl'],
            url=row['url'],
            tags=row['tags'],
            avgSentiment=row['avg_sentiment'],
            predictedSentiment=row['predicted_sentiment'],
            distance=row['distance'],
            reviews=[ReviewDto(**review) for review in reviews_with_scores] if reviews_with_scores else None
            # reviews=[ReviewDto(**review) for review in row['reviews']] if row['reviews'] else None
        )
        suggestion_result.append(destination_dto)
    return suggestion_result


def escape_special_characters(value: str) -> str:
    # List of special characters to escape
    special_characters = r'^[]{}()\\.*+?|'
    # Escape special characters using regex
    escaped_value = re.sub(f'([{re.escape(special_characters)}])', r'\\\1', value)
    return escaped_value


async def get_all_destinations(page: int, limit: int, search: str = None) -> DestinationPageDto:
    start_index = (page - 1) * limit
    end_index = start_index + limit

    destinations_data = await load_dataset()
    filtered_destinations = destinations_data

    # Parse the search query string if provided
    if search:
        # Parse the search query string to extract field-value pairs
        search_params = urllib.parse.parse_qs(search)

        # Filter the destinations based on the provided fields
        for field, value in search_params.items():
            if field in destinations_data.columns:
                # Convert values to lowercase for case-insensitive comparison
                value_lower = escape_special_characters(value[0].lower())
                filtered_destinations = filtered_destinations[
                    filtered_destinations[field].str.lower().str.contains(value_lower)]

    # Check if end_index is greater than the length of filtered_destinations
    end_index = min(end_index, len(filtered_destinations))

    # Convert filtered destination data to DestinationDto objects
    destinations_dto: [DestinationDto] = []
    for index, row in filtered_destinations[start_index:end_index].iterrows():

        try:
            reviews_with_scores = []
            for idx, review in enumerate(row['reviews']):
                review_with_score = review.copy()  # Create a copy of the review dictionary
                review_with_score['predictedSentiment'] = 0  # Assign sentiment score to userRating
                reviews_with_scores.append(review_with_score)

            destination_dto = DestinationDto(
                id=row['id'],
                code=row['code'],
                name=row['name'],
                price=row['price'],
                type=row['type'],
                districtName=row['districtName'],
                rating=row['rating'],
                reviewCount=len(row.get('reviews', 0)),
                gglat=row['gglat'],
                gglon=row['gglon'],
                imageUrl=row['imageUrl'],
                url=row['url'],
                tags=row['tags'],
                reviews=[ReviewDto(**review) for review in reviews_with_scores] if reviews_with_scores else None
            )
            destinations_dto.append(destination_dto)
        except Exception as e:
            print(f"Error processing row : {e}")

    data = DestinationPageDto(data=destinations_dto, totalRecord=len(filtered_destinations))
    return data


async def get_all_preferences(name) -> [str]:
    destinations_data = await load_dataset()

    # Get all tags from the dataset
    all_tags = []
    for index, row in destinations_data.iterrows():
        tags = row.loc["tags"]
        all_tags.extend(tags)

    # Convert to a set to remove duplicates
    unique_tags = set(all_tags)

    # Perform search if a name is provided
    if name:
        search_result = [tag for tag in unique_tags if name.lower() in tag.lower()]
    else:
        search_result = list(unique_tags)

    return search_result
