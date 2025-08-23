# Import necessary modules from constraints.py
from constraints import UserPreferences, Constraint, Preference
from dataclasses import dataclass

@dataclass
class Listing:
    id: str
    price: int
    sqft: int
    beds: int
    baths: float #should only be wholes or halves (ex, 2, 2.5, 1, 1.5 baths)
    city: str
    style: set[str] # {"modern", "traditional", ..., etc}, 
    listing_type: str        #"single", "family", "condo", etc.
    tenure: str             #"buy" or "rent"

class HousingRecommender:

    #add __init__? pass a copy of constraints (for manipulation purposes) and keep track of listing scores

    def filter_listings(self, listings, user_preferences):
        #SRY FOR THE BAD CODING PRACTICES BUT WE CAN FIX LATER
        #BASICALLY, WE FILTER OUT LISTINGS THAT DON'T MEET USER PREFERENCES
        #EXCLUDING ANY CONSTRAINTS THAT GOT REMOVED (value = NONE)
        filtered_listings = []
        for listing in listings:

            #does the city location match?
            if not (listing.city == user_preferences.constraints[Constraint.LOCATION].get_preference_value() and user_preferences.constraints[Constraint.LOCATION].get_preference_value != None):
            #print("Listing failed location constraint")
                continue


            #is the minimum sqFT met? or is it within reasonable flexibility?
            differenceInFeet = abs(listing.sqft - user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value())
            roomForError = 0
            if user_preferences.is_flexible(Constraint.SQUARE_FEET):
                roomForError = user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value() - (user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value() * user_preferences.constraints[Constraint.SQUARE_FEET].rigidity)

            if not (user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value() != None):
                    
                    if not (listing.sqft >= user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value() or
                (user_preferences.is_flexible(Constraint.SQUARE_FEET) and differenceInFeet <= roomForError)):
                        #print("Listing failed square feet constraint")
                        continue


            #is the price within budget? or, is it within reasonable flexibility?
            differenceInPrice = abs(listing.price - user_preferences.constraints[Constraint.BUDGET].get_preference_value())
            roomForError = 0
            if user_preferences.is_flexible(Constraint.BUDGET):
                roomForError = user_preferences.constraints[Constraint.BUDGET].get_preference_value() - (user_preferences.constraints[Constraint.BUDGET].get_preference_value() * user_preferences.constraints[Constraint.BUDGET].rigidity)

            if not (user_preferences.constraints[Constraint.LOCATION].get_preference_value() != None):

                if not (listing.price <= user_preferences.constraints[Constraint.BUDGET].get_preference_value() or
                    (user_preferences.is_flexible(Constraint.BUDGET) and differenceInPrice <= roomForError)):
                    #print("Listing failed budget constraint")
                    continue

            #go through all the styles we like. if none matches the constraints, dont add this property
            for style in user_preferences.constraints[Constraint.STYLE].get_preference_value():
                foundStyle = False
                if style in listing.style:
                    foundStyle = True
                    break
            if not foundStyle:
                #print("Listing failed style constraint")
                continue

            #TO-DO: MAYBE ADD SAME LOGIC TO BED/BATHS!!!!!

            #it meets our constraints, add it to the filtered list
            filtered_listings.append(listing)
        return filtered_listings


    #Returns the 1st matching suitable listing for the user <- MAYBE CHANGE?
    def recommend_listing(self, user_preferences, listings):
        filtered_listings = self.filter_listings(listings, user_preferences)

        #if no listings found after filtering through constraints, drop the most flexible constraint and try again
        if not filtered_listings: 
            self.drop_most_rigid_constraint(user_preferences)
            try:
                return self.recommend_listing(user_preferences, listings)  #recursive call after dropping current most flexible constraint
            except RecursionError:
                print("No suitable homes found!")
                return []
        return filtered_listings[0]




    #drops most rigid constraint to open up options for a search
    def drop_most_rigid_constraint(self, user_preferences):
        most_rigid_constraint = None
        max_rigidity = -1
        for constraint in user_preferences.constraints:
            if constraint != Constraint.BUY_OR_RENT and user_preferences.constraints[constraint].rigidity > max_rigidity:
                most_rigid_constraint = constraint
                max_rigidity = user_preferences.constraints[constraint].rigidity
        if most_rigid_constraint is not None:
            user_preferences.remove_constraint(most_rigid_constraint)




    #**only** used after if a constraint is removed (value = none, rigid = -1), and we want to re-add it
    def reinstate_user_constraint(self, user_preferences, constraint: Constraint, value, rigidity):
        user_preferences.reAdd_constraint(constraint, value, rigidity)

    #allows user to like/dislike a listing
    def update_user_feedback(self, user_preferences, listing: Listing, liked: bool):
        """
        IDEA: give each listing a score of 1 (worst match) to 5 (best match)
        Score is based on how well listing meets user preferences (excluding buy_or_rent), weighted by rigidity score
            ex, if a listing is a "condo" (preferred) in "Santa Cruz" (preferred location) with 3 beds (preferred) and 2 baths (preferred), it might get a score of 5
            ex, if a listing is a "house" (not preferred, rigid 0.1) in "Santa Cruz" (prefered) with 3 beds (prefered) and 2 bath (prefered), it might get a score of 3.5
                this is bc the home type has a rigidity score of 0.1, meaning it is very important to match, which lowers its overall score
                on the other hand, if rigidity was 1, it might have been a 4.5 since the location is flexible and not important to the user

        Score is updated based on like/disliking a house
            if the user likes the listing, increase its score and those with similar properties
                the more in common, the higher the increase
            if the user dislikes the listing, decrease its score and those with similar properties
                the more in common, the higher the decrease
        """
        if liked:
            pass
        else:
            pass

# Example usage
if __name__ == '__main__':


    listings = [
        Listing(id="L001", price=250000, sqft=800, beds=3, baths=2.5, city="Los Angeles", style="Modern", listing_type="Apartment", tenure="buy"),
        Listing(id="L002", price=700000, sqft=3000, beds=4, baths=3, city="New York", style="Traditional", listing_type="House", tenure="rent"),
        Listing(id="L003", price=500000, sqft=1500, beds=3, baths=2, city="Chicago", style="Contemporary", listing_type="Condo", tenure="buy"),
        Listing(id="L004", price=1600000, sqft=1800, beds=3, baths=2.5, city="San Francisco", style="Spanish", listing_type="Condo", tenure="buy"),
        Listing(id="L005", price=1000000, sqft=2000, beds=3, baths=1.5, city="Santa Cruz", style="Victorian", listing_type="Suite", tenure="buy"),
        Listing(id="L006", price=800000, sqft=2200, beds=4, baths=3, city="Los Angeles", style="Modern", listing_type="House", tenure="rent")
    ]
    
    user_preferences = UserPreferences()
    user_preferences.update_constraint_value(Constraint.HOME_TYPE, {"single", "condo", "family"})
    user_preferences.update_constraint_value(Constraint.STYLE, {"modern", "spanish", "Victorian"})
    user_preferences.update_constraint_value(Constraint.LOCATION, "Santa Cruz")
    user_preferences.update_constraint_value(Constraint.SQUARE_FEET, 1000)
    user_preferences.update_constraint_value(Constraint.BUDGET, 1500000)

    system = HousingRecommender()

    recommended_listing = system.recommend_listing(user_preferences, listings)
    print(f"Initial Recommended Listing: {recommended_listing.id}, {recommended_listing.price}, {recommended_listing.city}")