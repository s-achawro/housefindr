# Import necessary modules from constraints.py
from constraints import UserPreferences, Constraint, Preference
from dataclasses import dataclass
import random

@dataclass
class Listing:
    id: str
    price: int
    sqft: int
    beds: int
    baths: float
    city: str
    style: set[str]
    listing_type: str
    tenure: str

class HousingRecommender:

    #add __init__?
    def __init__(self):
        self.weights = {
            "location":    0.25,
            "home_type":   0.25,
            "square_feet": 0.25,
            "budget":      0.25,
            "style":       0.00,
        }
        self.learning_rate = 0.12
        self.exclude_ids = set()
        self.top_k = 3
        self.explore_epsilon = 0.15

    # ====== AI helpers  ======
    def _normalize_weights(self):
        for k in self.weights:
            self.weights[k] = max(0.0, min(1.0, self.weights[k]))
        s = sum(self.weights.values())
        if s == 0:
            n = len(self.weights)
            for k in self.weights:
                self.weights[k] = 1.0 / n
        else:
            for k in self.weights:
                self.weights[k] /= s

    def _imp(self, user_preferences, constraint: Constraint) -> float:
        r = getattr(user_preferences.constraints[constraint], "rigidity", 0.0)
        base = 1.0 - max(0.0, min(1.0, r))
        return 0.75 + 0.25 * base

    def _sim_budget(self, price: int, max_budget: float) -> float:
        if not (isinstance(max_budget, (int, float)) and max_budget > 0):
            return 0.0
        if price <= max_budget:
            return 1.0 - (max_budget - price) / (max_budget + 1e-9) * 0.15
        over = (price - max_budget) / (max_budget + 1e-9)
        return max(0.0, 1.0 - 1.25 * over)

    def _sim_sqft(self, sqft: int, min_sqft: float) -> float:
        if not (isinstance(min_sqft, (int, float)) and min_sqft > 0):
            return 0.0
        if sqft >= min_sqft:
            surplus = (sqft - min_sqft) / (min_sqft + 1e-9)
            return min(1.0, 0.7 + 0.3 * min(1.0, surplus))
        gap = (min_sqft - sqft) / (min_sqft + 1e-9)
        return max(0.0, 1.0 - 1.5 * gap)

    def _match_location(self, listing_city: str, wanted_city: str) -> float:
        if not isinstance(wanted_city, str) or not wanted_city:
            return 0.0
        return 1.0 if listing_city == wanted_city else 0.0

    def _match_home_type(self, listing_type: str, pref) -> float:
        if isinstance(pref, set):
            return 1.0 if listing_type in pref else 0.0
        if isinstance(pref, str) and pref:
            return 1.0 if listing_type == pref else 0.0
        return 0.0

    def _match_style(self, listing_styles, pref) -> float:
        # tolerate strings in either field
        if isinstance(listing_styles, str):
            listing_styles = {listing_styles}
        if isinstance(pref, str):
            pref = {pref}
        if isinstance(pref, set) and len(pref) > 0:
            return 1.0 if len(listing_styles & pref) > 0 else 0.0
        return 0.0

    def score_listing(self, listing: Listing, user_preferences: UserPreferences) -> float:
        budget_pref = user_preferences.constraints[Constraint.BUDGET].get_preference_value()
        sqft_pref   = user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value()
        loc_pref    = user_preferences.constraints[Constraint.LOCATION].get_preference_value()
        type_pref   = user_preferences.constraints[Constraint.HOME_TYPE].get_preference_value()
        style_pref  = user_preferences.constraints[Constraint.STYLE].get_preference_value()

        s_budget = self._sim_budget(listing.price, budget_pref)
        s_sqft   = self._sim_sqft(listing.sqft, sqft_pref)
        s_loc    = self._match_location(listing.city, loc_pref)
        s_type   = self._match_home_type(listing.listing_type, type_pref)
        s_style  = self._match_style(listing.style, style_pref)

        i_budget = self._imp(user_preferences, Constraint.BUDGET)
        i_sqft   = self._imp(user_preferences, Constraint.SQUARE_FEET)
        i_loc    = self._imp(user_preferences, Constraint.LOCATION)
        i_type   = self._imp(user_preferences, Constraint.HOME_TYPE)
        i_style  = self._imp(user_preferences, Constraint.STYLE)

        score = (
            self.weights["budget"]      * i_budget * s_budget +
            self.weights["square_feet"] * i_sqft   * s_sqft   +
            self.weights["location"]    * i_loc    * s_loc    +
            self.weights["home_type"]   * i_type   * s_type   +
            self.weights["style"]       * i_style  * s_style
        )
        return float(score)

    def filter_listings(self, listings, user_preferences):
        #SRY FOR THE BAD CODING PRACTICES BUT WE CAN FIX LATER
        #BASICALLY, WE FILTER OUT LISTINGS THAT DON'T MEET USER PREFERENCES
        #EXCLUDING ANY CONSTRAINTS THAT GOT REMOVED (value = NONE)
        filtered_listings = []
        for listing in listings:

            #does the city location match?
            loc_val = user_preferences.constraints[Constraint.LOCATION].get_preference_value() 
            if isinstance(loc_val, str) and loc_val != "":
                if listing.city != loc_val:
                    continue

            #is the minimum sqFT met? or is it within reasonable flexibility?
            sqft_val = user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value()
            if isinstance(sqft_val, (int, float)) and sqft_val > 0:
                differenceInFeet = abs(listing.sqft - sqft_val)
                roomForError = 0
                if user_preferences.is_flexible(Constraint.SQUARE_FEET):
                    r = user_preferences.constraints[Constraint.SQUARE_FEET].rigidity
                    roomForError = sqft_val - (sqft_val * r)
                if not (listing.sqft >= sqft_val or
                        (user_preferences.is_flexible(Constraint.SQUARE_FEET) and differenceInFeet <= roomForError)):
                    #print("Listing failed square feet constraint")
                    continue

            #is the price within budget? or, is it within reasonable flexibility?
            bud_val = user_preferences.constraints[Constraint.BUDGET].get_preference_value()
            if isinstance(bud_val, (int, float)) and bud_val > 0:
                differenceInPrice = abs(listing.price - bud_val)
                roomForError = 0
                if user_preferences.is_flexible(Constraint.BUDGET):
                    r = user_preferences.constraints[Constraint.BUDGET].rigidity
                    roomForError = bud_val - (bud_val * r)
                if not (listing.price <= bud_val or
                        (user_preferences.is_flexible(Constraint.BUDGET) and differenceInPrice <= roomForError)):
                    #print("Listing failed budget constraint")
                    continue

            #go through all the styles we like. if none matches the constraints, dont add this property
            pref_styles = user_preferences.constraints[Constraint.STYLE].get_preference_value()
            if isinstance(pref_styles, set) and len(pref_styles) > 0:
                listing_styles = listing.style if isinstance(listing.style, set) else {listing.style}
                if listing_styles.isdisjoint(pref_styles):
                    #print("Listing failed style constraint")
                    continue

            #TO-DO: MAYBE ADD SAME LOGIC TO BED/BATHS!!!!!

            #it meets our constraints, add it to the filtered list
            filtered_listings.append(listing)
        return filtered_listings

    #Returns the 1st matching suitable listing for the user
    def recommend_listing(self, user_preferences, listings):
        # --- replaced with scoring + exploration like recommender.py ---
        candidates = [l for l in listings if l.id not in self.exclude_ids]
        if not candidates:
            candidates = listings

        candidates = self.filter_listings(candidates, user_preferences)

        scored = [(self.score_listing(l, user_preferences), l) for l in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored or scored[0][0] <= 0:
            print("No suitable homes found!")
            return None

        pool = [l for _, l in scored[:min(self.top_k, len(scored))]]
        if len(pool) > 1 and random.random() < self.explore_epsilon:
            return random.choice(pool[1:])
        return pool[0]

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
        budget_pref = user_preferences.constraints[Constraint.BUDGET].get_preference_value()
        sqft_pref   = user_preferences.constraints[Constraint.SQUARE_FEET].get_preference_value()
        loc_pref    = user_preferences.constraints[Constraint.LOCATION].get_preference_value()
        type_pref   = user_preferences.constraints[Constraint.HOME_TYPE].get_preference_value()
        style_pref  = user_preferences.constraints[Constraint.STYLE].get_preference_value()

        s_budget = self._sim_budget(listing.price, budget_pref)
        s_sqft   = self._sim_sqft(listing.sqft, sqft_pref)
        s_loc    = self._match_location(listing.city, loc_pref)
        s_type   = self._match_home_type(listing.listing_type, type_pref)
        s_style  = self._match_style(listing.style, style_pref)

        g = self.learning_rate if liked else -self.learning_rate

        self.weights["budget"]      += g * s_budget
        self.weights["square_feet"] += g * s_sqft
        self.weights["location"]    += g * s_loc
        self.weights["home_type"]   += g * s_type
        self.weights["style"]       += g * s_style

        if not liked:
            self.exclude_ids.add(listing.id)

        self._normalize_weights()


def interactive_loop(system, prefs, listings):
    print(prefs)
    while True:
        rec = system.recommend_listing(prefs, listings)
        if not rec:
            print("No recommendation found. Try loosening constraints.")
            break

        print(f"\nRecommended: {rec.id} | ${rec.price} | {rec.city} | {rec.listing_type} | styles={rec.style}")
        ans = input("Do you like this listing? [y/n/q]: ").strip().lower()
        if ans == "q":
            break

        liked = (ans == "y")
        system.update_user_feedback(prefs, rec, liked)
        print("Updated weights:", {k: round(v, 3) for k, v in system.weights.items()})

# Example usage
if __name__ == '__main__':

    listings = [
        # converted style values to sets for consistency
        Listing(id="L001", price=250000, sqft=800,  beds=3, baths=2.5, city="Los Angeles",   style={"Modern"},       listing_type="Apartment", tenure="buy"),
        Listing(id="L002", price=700000, sqft=3000, beds=4, baths=3,   city="New York",      style={"Traditional"},  listing_type="House",     tenure="rent"),
        Listing(id="L003", price=500000, sqft=1500, beds=3, baths=2,   city="Chicago",       style={"Contemporary"}, listing_type="Condo",     tenure="buy"),
        Listing(id="L004", price=1600000, sqft=1800, beds=3, baths=2.5, city="San Francisco", style={"Spanish"},     listing_type="Condo",     tenure="buy"),
        Listing(id="L005", price=1000000, sqft=2000, beds=3, baths=1.5, city="Santa Cruz",    style={"Victorian"},   listing_type="Suite",     tenure="buy"),
        Listing(id="L006", price=800000,  sqft=2200, beds=4, baths=3,   city="Los Angeles",   style={"Modern"},       listing_type="House",     tenure="rent"),



        Listing(id="LLA01", price=650000,  sqft=1100, beds=2, baths=2.0, city="Los Angeles", style={"Modern"},     listing_type="Apartment", tenure="buy"),
        Listing(id="LLA02", price=700000,  sqft=1200, beds=2, baths=2.0, city="Los Angeles", style={"Spanish"},    listing_type="Apartment", tenure="buy"),
        Listing(id="LLA03", price=590000,  sqft=1000, beds=1, baths=1.5, city="Los Angeles", style={"Victorian"},  listing_type="Apartment", tenure="buy"),

        # Condos
        Listing(id="LLA04", price=900000,  sqft=1400, beds=2, baths=2.0, city="Los Angeles", style={"Modern"},     listing_type="Condo",     tenure="buy"),
        Listing(id="LLA05", price=1050000, sqft=2000, beds=3, baths=2.5, city="Los Angeles", style={"Modern"},     listing_type="Condo",     tenure="buy"),
        Listing(id="LLA06", price=720000,  sqft=1300, beds=2, baths=2.0, city="Los Angeles", style={"Spanish"},    listing_type="Condo",     tenure="buy"),

        # Houses
        Listing(id="LLA07", price=1200000, sqft=1800, beds=3, baths=2.5, city="Los Angeles", style={"Victorian"},  listing_type="House",     tenure="buy"),
        Listing(id="LLA08", price=1350000, sqft=2400, beds=4, baths=3.0, city="Los Angeles", style={"Spanish"},    listing_type="House",     tenure="buy"),
        Listing(id="LLA09", price=950000,  sqft=1700, beds=3, baths=2.0, city="Los Angeles", style={"Spanish"},    listing_type="House",     tenure="buy"),
        Listing(id="LLA10", price=1450000, sqft=2600, beds=4, baths=3.0, city="Los Angeles", style={"Victorian"},  listing_type="House",     tenure="buy"),
        Listing(id="LLA11", price=800000,  sqft=2200, beds=4, baths=3.0, city="Los Angeles", style={"Modern"},     listing_type="House",     tenure="rent"),  # rent to test tenure
        Listing(id="LLA12", price=1600000, sqft=3000, beds=5, baths=3.5, city="Los Angeles", style={"Modern"},     listing_type="House",     tenure="buy"),

    ]
    
    user_preferences = UserPreferences()
    # align labels with listing data so scoring can match home types/styles
    user_preferences.update_constraint_value(Constraint.HOME_TYPE, {"Apartment", "Condo", "House"})
    user_preferences.update_constraint_value(Constraint.STYLE, {"Modern", "Spanish", "Victorian"})
    user_preferences.update_constraint_value(Constraint.LOCATION, "Los Angeles")
    user_preferences.update_constraint_value(Constraint.SQUARE_FEET, 1000)
    user_preferences.update_constraint_value(Constraint.BUDGET, 1500000)

    system = HousingRecommender()

    # interactive like/dislike loop (same UX as recommender.py)
    interactive_loop(system, user_preferences, listings)

    # If you want the one-shot behavior back, you can still do:
    # recommended_listing = system.recommend_listing(user_preferences, listings)
    # print(f"Initial Recommended Listing: {recommended_listing.id}, {recommended_listing.price}, {recommended_listing.city}")
