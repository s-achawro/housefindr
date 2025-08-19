import Algorithm
import constraints
from constraints import Constraint, PurchaseType
import math
import sqlite3
import random

from geopy.geocoders import Nominatim

def havDist(lat1, lon1, lat2, lon2):
  """
  Haversine dist of two lat/long points
  """
  R = 3958.8  # Radius of Earth in miles

  lat1Rad = math.radians(lat1)
  lon1Rad = math.radians(lon1)
  lat2Rad = math.radians(lat2)
  lon2Rad = math.radians(lon2)

  dlon = lon2Rad - lon1Rad
  dlat = lat2Rad - lat1Rad

  a = math.sin(dlat / 2)**2 + math.cos(lat1Rad) * math.cos(lat2Rad) * math.sin(dlon / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

  distance = R * c
  return distance


class UTAlgorithm:
    def __init__(self):
        connection = sqlite3.connect("houselisting.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM listings")  
        self.database = cursor.fetchall()
        self.build_listings_from_db()
        connection.close()

        self.constraints = constraints.UserPreferences()
        self.algorithm = Algorithm.HousingRecommender([parameter for parameter in self.constraints.get_constraints().values()])

        self.feed = [] #[current, next, n2, n3, ..., n6]
                    #feed += algorithm.feedback + algorithm.recommend, pop from front


    def build_listings_from_db(self):
        self.listings = []
        for row in self.database:
            house = Algorithm.Listing(
                id=row[0],
                price=row[4],
                sqft=row[8],
                beds=row[6],
                baths=row[7],
                city=row[10],
                listing_type=row[2], #MISSING FROM DB
                tenure=row[3],
                is_sold=row[2] #MISSING FROM DB
            )
            self.listings.append(house)
        self.database = self.listings


    #===GETTERS===#
    def get_user_preferences(self):
        return self.constraints.get_constraints()

    def return_database(self):
        return self.database
    
    #===SETTERS===#
    def update_rigidity(self, constraint, value):
        self.constraints.update_constraint_rigidity(constraint, value)
        self.algorithm.constraints = self.constraints

    def update_constraint(self, constraint, value):
        self.constraints.update_constraint_value(constraint, value)
        self.algorithm.constraints = self.constraints

    #===PRINTS===#
    def print_constraints(self):
        self.constraints.print_constraints()

    def print_database(self):
        for row in self.database:
            print(row)

    #===ALGORITHM STUFF===#
    def recommend_homes(self):
        print(len(self.feed))
        for i in range(2):
            sorting = self.algorithm.recommend(self.return_database())
            print(self.return_database())

            self.feed.append(sorting[i])

    def receive_user_feedback(self, feedback):
        current = self.feed[0]
        self.algorithm.feedback(current, feedback)
        self.feed.pop(0)


    def process_input(self, user_input):
        if user_input.lower() == "like":
            self.receive_user_feedback(True)
        elif user_input.lower() == "dislike":
            self.receive_user_feedback(False)

        self.recommend_homes()

    def run(self):
        self.recommend_homes()
        home = random.choice(self.database)
        if len(self.feed) != 0:
            print("Current home:", self.feed[0])
            home = self.feed[0]
        else:
            print("Random Home: ", home)

        while True:
            user_input = input("Type 'Like' or 'Dislike' on this house. Or, type 'EXIT' if you are done: ")
            if user_input.lower() == "exit":
                break
            elif user_input.lower() not in ["like", "dislike"]:
                print("Invalid input. Please type 'Like', 'Dislike', or 'EXIT'.")
                continue
            else:
                self.process_input(home, user_input)

if __name__ == "__main__":

    ut_algorithm = UTAlgorithm()
    ut_algorithm.update_constraint(Constraint.HOME_TYPE, {"single", "condo", "family"})
    ut_algorithm.update_constraint(Constraint.LOCATION, "Los Angeles")
    ut_algorithm.update_constraint(Constraint.SQUARE_FEET, 1000)
    ut_algorithm.update_constraint(Constraint.BUDGET, 500000)

    print(ut_algorithm.algorithm.constraints)

    ut_algorithm.run()

    """
    geolocator = Nominatim(user_agent="my_geocoder_app")
    address1 = "1600 Amphitheatre Parkway, Mountain View, CA"
    address2 = "1 Infinite Loop, Cupertino, CA"

    location1 = geolocator.geocode(address1)
    location2 = geolocator.geocode(address2)

    if location1 and location2:
        l1lat = location1.latitude
        l1lon = location1.longitude
        l2lat = location2.latitude
        l2lon = location2.longitude

        print(havDist(l1lat, l1lon, l2lat, l2lon))
    else:
        print("Location not found")
    """

