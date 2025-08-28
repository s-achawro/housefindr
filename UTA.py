import algorithm
import constraints
from constraints import Constraint, PurchaseType
import math
import sqlite3
import random
from PIL import Image
import requests
from io import BytesIO


def display_image_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        
        image.show()
    else:
        print(f"Failed to retrieve the image. Status code: {response.status_code}")

class UTAlgorithm:
    def __init__(self):
        

        ###DO NOT TOUCH, FOR DB PROPAGATION###

        self.idToImg = {}


        connection = sqlite3.connect("houselisting.db")
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM listings")  
        self.database = cursor.fetchall()
        self.build_listings_from_db()

        cursor.execute("SELECT * FROM images")
        self.idToImg = cursor.fetchall()
        self.grab_images_from_db()
        connection.close()
        ###DO NOT TOUCH, FOR DB PROPAGATION###

        self.constraints = constraints.UserPreferences()
        self.algorithm = algorithm.HousingRecommender()

        self.feed = [] #[current, next, n2, n3, ..., n6]
                    #feed += algorithm.feedback + algorithm.recommend, pop from front

    ###DO NOT TOUCH, FOR DB PROPAGATION###
    #auto-propagates all possible listings from database
    def build_listings_from_db(self):
        self.listings = []
        for row in self.database:
            house = algorithm.Listing(
                id=str(row[0]),
                price=row[4],
                sqft=row[8],
                beds=row[6],
                baths=row[7],
                city=row[10],
                style=row[-2],
                listing_type=row[-3],
                tenure=row[3],
            )
            self.listings.append(house)

        self.database = self.listings

    def grab_images_from_db(self):
        images = {}
        for row in self.idToImg:
            images[str(row[0])] = row[2]  #map id to image url
        self.idToImg = images
    ###DO NOT TOUCH, FOR DB PROPAGATION###


    #===GETTERS===#
    def get_user_preferences(self):
        return self.constraints.get_constraints()

    def return_database(self):
        return self.database
    
    def get_current_home(self):
        if self.feed:
            return self.feed[0]
        else:
            return None
        
    def get_home(self, ID):
        for home in self.database:
            if home.id == ID:
                return home
        return None
    

    def get_current_url(self):
        home = self.get_current_home()
        if home:
            return self.idToImg[home.id]
        return None

    def get_home_url(self, ID):
        return self.idToImg[ID]

    #===SETTERS===#
    def update_rigidity(self, constraint, value):
        self.constraints.update_constraint_rigidity(constraint, value)
        self.algorithm.constraints = self.constraints.get_constraints()

    def update_constraint(self, constraint, value):
        self.constraints.update_constraint_value(constraint, value)
        self.algorithm.constraints = self.constraints.get_constraints()

    #===PRINTS===#
    def print_constraints(self):
        self.constraints.print_constraints()

    def print_database(self):
        for row in self.database:
            print(row)

    def print_home(self, ID):
        home = self.get_home(ID)
        if home:
            print(home)
        else:
            print("Home not found.")

    def print_current_home(self):
        home = self.get_current_home()
        if home:
            print(home)
        else:
            print("No current home.")

    #img display
    def show_current_home(self):
        home = self.get_current_home()
        if home:
            display_image_from_url(self.idToImg[home.id])
        else:
            print("No current home.")
    #img display
    def show_home(self, ID):
        home = self.get_home(ID)
        if home:
            display_image_from_url(self.idToImg[home.id])
        else:
            print("Home not found.")

    #===ALGORITHM STUFF===#

    def reccomend_2_homes(self):
        recs = []
        for _ in range(2):
            rec = self.algorithm.recommend_listing(self.constraints, self.database)
            if rec:
                recs.append(rec)
                self.database.remove(rec) #remove from pool to avoid duplicates
                print(self.get_home(rec.id))
        if len(self.feed) <= 5: #max size of 7
            self.feed += recs


    #main loop, use to run system
    #taken from algorithm.py interactive_loop, modified to for simplicity to interact with frontend
    def run(self):
        while True:
            self.reccomend_2_homes()
            rec = self.get_current_home()
            if not rec:
                print("No recommendation found. Try loosening constraints.")
                break
            print(f"\nRecommended: {rec.id} | ${rec.price} | {rec.city} | {rec.listing_type} | styles={rec.style}")
            #self.show_current_home() #<- IMG DISPLAY FOR RUNNING IN CONSOLE
            ans = input("Do you like this listing? [y/n/q]: ").strip().lower()
            if ans == "q":
                break

            liked = (ans == "y")
            self.algorithm.update_user_feedback(self.constraints, rec, liked)
            print("Updated weights:", {k: round(v, 3) for k, v in self.algorithm.weights.items()})
            self.feed.pop(0)


if __name__ == "__main__":
    

    ut_algorithm = UTAlgorithm()
    ut_algorithm.update_constraint(Constraint.HOME_TYPE, {"single", "condo", "family"})
    ut_algorithm.update_constraint(Constraint.STYLE, {"modern", "spanish", "victorian"})
    ut_algorithm.update_constraint(Constraint.LOCATION, "San Jose")
    ut_algorithm.update_constraint(Constraint.SQUARE_FEET, 1000)
    ut_algorithm.update_constraint(Constraint.BUDGET, 2000000)

    ut_algorithm.run()


