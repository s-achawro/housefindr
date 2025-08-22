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
    style: str | set[str] #"spanish", OR, {"modern", "traditional", ..., etc}, 
    listing_type: str        #"single", "family", "condo", etc.
    tenure: str             #"buy" or "rent"

def filter_listings(listings, user_preferences):
    filtered_listings = []
    for listing in listings:

        if not (listing.city == user_preferences.constraints[Constraint.LOCATION].value or
            user_preferences.constraints[Constraint.LOCATION].rigidity <= 0):
           continue
        if not (listing.listing_type == user_preferences.constraints[Constraint.HOME_TYPE].value or
            user_preferences.constraints[Constraint.HOME_TYPE].rigidity <= 0):
           continue

        differenceInFeet = abs(listing.sqft - user_preferences.constraints[Constraint.SQUARE_FEET].value)
        roomForError = 0
        if user_preferences.constraints[Constraint.SQUARE_FEET].rigidity > 0:
            roomForError = differenceInFeet - (user_preferences.constraints[Constraint.SQUARE_FEET].value * user_preferences.constraints[Constraint.SQUARE_FEET].rigidity)
        if not (listing.sqft >= user_preferences.constraints[Constraint.SQUARE_FEET].value or
            (user_preferences.constraints[Constraint.SQUARE_FEET].rigidity <= 0 and differenceInFeet <= roomForError)):
           continue

        differenceInPrice = abs(listing.price - user_preferences.constraints[Constraint.BUDGET].value)
        roomForError = 0
        if user_preferences.constraints[Constraint.BUDGET].rigidity > 0:
            roomForError = differenceInPrice - (user_preferences.constraints[Constraint.BUDGET].value * user_preferences.constraints[Constraint.BUDGET].rigidity)
        if not (listing.price <= user_preferences.constraints[Constraint.BUDGET].value or
            (user_preferences.constraints[Constraint.BUDGET].rigidity <= 0 and differenceInPrice <= roomForError)):
           continue

        filtered_listings.append(listing)
    return filtered_listings

def recommend_listing(user_preferences, listings):
    filtered_listings = filter_listings(listings, user_preferences)
    if not filtered_listings:
        drop_most_rigid_constraint(user_preferences)
        return recommend_listing(user_preferences, listings)  #recursive call
    return filtered_listings[0]

def drop_most_rigid_constraint(user_preferences):
    most_rigid_constraint = None
    max_rigidity = -1
    for constraint in user_preferences.constraints:
        if constraint != Constraint.BUY_OR_RENT and user_preferences.constraints[constraint].rigidity > max_rigidity:
            most_rigid_constraint = constraint
            max_rigidity = user_preferences.constraints[constraint].rigidity
    if most_rigid_constraint is not None:
        user_preferences.update_constraint_value(most_rigid_constraint, "")
        user_preferences.update_constraint_rigidity(most_rigid_constraint, 0)

def update_user_feedback(user_preferences, listing: Listing, liked: bool):
    if liked:
        pass
    else:
        user_preferences.update_constraint_rigidity(Constraint.LOCATION, max(user_preferences.constraints[Constraint.LOCATION].rigidity, 0.1))

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
    user_preferences.update_constraint_value(Constraint.STYLE, {"modern", "spanish", "victorian"})
    user_preferences.update_constraint_value(Constraint.LOCATION, "San Jose")
    user_preferences.update_constraint_value(Constraint.SQUARE_FEET, 1000)
    user_preferences.update_constraint_value(Constraint.BUDGET, 1500000)

    recommended_listing = recommend_listing(user_preferences, listings)
    print(f"Initial Recommended Listing: {recommended_listing.id}, {recommended_listing.price}, {recommended_listing.city}")

    #user_feedback = get_user_feedback()
    #update_user_feedback(user_preferences, recommended_listing, user_feedback)