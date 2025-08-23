import algorithm
import constraints
from constraints import Constraint, PurchaseType
import math
import sqlite3
import random

"""
INITIAL PLAN/CONCEPT:
push 2 recommended homes to the feed at a time
every time the user provides feedback, the scoring updates, and pushes 2 new homes into the feed
front of feed = current item user is looking at/currently being recommended, back of feed = upcoming homes to recommend based on feedback
    
IMPORTANT-Q: how to deal with making sure we dont get duplicates/recommend the same home multiple times?

note: have not tested/touched since working on algorithm.py
"""

class UTAlgorithm:
    def __init__(self):


        ###DO NOT TOUCH, FOR DB PROPAGATION###
        connection = sqlite3.connect("houselisting.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM listings")  
        self.database = cursor.fetchall()
        self.build_listings_from_db()
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
    ###DO NOT TOUCH, FOR DB PROPAGATION###


    #===GETTERS===#
    def get_user_preferences(self):
        return self.constraints.get_constraints()

    def return_database(self):
        return self.database
    
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

    #===ALGORITHM STUFF===#
    def recommend_homes(self):
        #adds 2 recommended homes to the feed at a time based on previous user feedback
        for i in range(2):
            sorting = self.algorithm.recommend(self.return_database())
            
            try:
                self.feed.append(sorting[i])
            except IndexError:
                continue
    
    def receive_user_feedback(self, home, feedback):
        #process feedback for the current home, and removes it from feed
        self.algorithm.feedback(home, feedback)
        self.feed.remove(home)


    def process_input(self, home, user_input):
        #processes user input
        if user_input.lower() == "like":
            self.receive_user_feedback(home, True)
        elif user_input.lower() == "dislike":
            self.receive_user_feedback(home, False)

        self.recommend_homes()

    #main loop, use to run system
    def run(self):
        self.recommend_homes()
        home = random.choice(self.database)
        if len(self.feed) != 0:
            home = self.feed[0]

        while True:
            print("Current home:", home)

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
    ut_algorithm.update_constraint(Constraint.STYLE, {"modern", "spanish", "victorian"})
    ut_algorithm.update_constraint(Constraint.LOCATION, "Santa Cruz")
    ut_algorithm.update_constraint(Constraint.SQUARE_FEET, 1000)
    ut_algorithm.update_constraint(Constraint.BUDGET, 2000000)

    ut_algorithm.run()


