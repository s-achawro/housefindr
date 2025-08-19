"""
For CMPM 146 Final Project
Data class of user preferences for searching for homes via a Tinder like real estate service
"""


from enum import Enum
from unittest import case

class PurchaseType(Enum):
    BUY = "buying"
    RENT = "renting"

class Constraint(Enum):
    LOCATION = "city"
    HOME_TYPE = "listing_type"
    SQUARE_FEET = "min_sqft"
    BUDGET = "max_price"
    BUY_OR_RENT = "tenure"
    INCLUDE_NOT_FOR_SALE = "include_sold"

class UserPreferences:
    """
    Data class to store and manage user preferences
    User preferences are stored in a dict, with the values as Preferences
    """
    def __init__(self):
        self.constraints = {
            Constraint.LOCATION: Preference("", 0.025), #city name
            Constraint.HOME_TYPE: Preference("", 0.2), #ex, "apartment", "house", "condo", etc
            Constraint.SQUARE_FEET: Preference(0.0, 0.01),
            Constraint.BUDGET: Preference(0, 0),
            Constraint.BUY_OR_RENT: Preference(PurchaseType.BUY, 0), #rigidity always 0, cant be removed
            Constraint.INCLUDE_NOT_FOR_SALE: Preference(False, 0) #rigidity always 0, cant be removed
        }


    #===SETTERS===#

    def update_constraint_value(self, constraint: Constraint, value):
        """
        Update the value of a specific constraint
        Each constraint and value pair must be valid for the specific constraint type in order to update
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")
        
        match constraint:
            case Constraint.LOCATION:
                if not isinstance(value, str):
                    raise ValueError("Location must be a city name (string).")
            case Constraint.HOME_TYPE:
                if (not isinstance(value, str)) and (not isinstance(value, set)):
                    raise ValueError("Home type must be a string or a set of strings.")
            case Constraint.SQUARE_FEET:
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError("Square feet must be a positive number.")
            case Constraint.BUDGET:
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError("Budget must be a positive number.")
            case Constraint.BUY_OR_RENT:
                if not isinstance(value, PurchaseType):
                    raise ValueError("Buy or rent must be a PurchaseType enum.")
            case Constraint.INCLUDE_NOT_FOR_SALE:
                if not isinstance(value, bool):
                    raise ValueError("'Include not for sale' must be a boolean.")

        self.constraints[constraint].update_user_preference(value)



    def update_constraint_rigidity(self, constraint: Constraint, rigidity: float):
        """
        Update the rigidity of a specific constraint
        Each constraint and rigidity pair must be valid for the specific constraint type in order to update
        In addition, rigidity must be a float between 0 and 1 (inclusive)

        CONDITIONS: Cannot update rigidity for 'buy_or_rent' or 'include_not_for_sale'
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")
        
        if constraint == Constraint.BUY_OR_RENT or constraint == Constraint.INCLUDE_NOT_FOR_SALE:
                raise ValueError("Rigidity for 'buy_or_rent' and 'include_not_for_sale' must always be 0.")

        if rigidity < 0 or rigidity > 1:
            raise ValueError("Rigidity must be between 0 and 1.")
        self.constraints[constraint].update_preference_rigidity(rigidity)





    #===GETTERS===#

    def get_constraints(self):
        """
        Get all user constraints
        """
        return {key.value: value.get_preferences() for key, value in self.constraints.items()}

    def get_single_constraint(self, constraint: Constraint):
        """
        Get a single user constraint
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")
        return {constraint.value: self.constraints[constraint].get_preferences()}
    
    def is_flexible(self, constraint: Constraint):
        """
        Returns if a specific constraint is flexible or not
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")

        if self.constraints[constraint].return_flexibility() > 0:
            return True
        return False




    #===REMOVE A CONSTRAINT===#


    def remove_constraint(self, constraint: Constraint):
        """
        Remove a user constraint
        CONDITIONS: Cannot remove 'buy_or_rent' or 'include_not_for_sale'
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")
        
        if constraint == Constraint.BUY_OR_RENT or constraint == Constraint.INCLUDE_NOT_FOR_SALE:
            raise ValueError("Cannot remove 'buy_or_rent' or 'include_not_for_sale' constraints.")
        self.constraints[constraint] = Preference(None, 1) #none object w/ 1 rigidity, it is no longer a constraint 



    #===PRINTS===#

    def print_constraints(self):
        """
        Print all user constraints
        """
        for key, value in self.constraints.items():
            print(f"{key.value}: {value.get_preferences()}")

    def print_single_constraint(self, constraint: Constraint):
        """
        Print a single user constraint
        """
        if constraint not in self.constraints:
            raise ValueError(f"Constraint '{constraint.value}' does not exist.")
        print(f"{constraint.value}: {self.constraints[constraint].get_preferences()}")

class Preference:
    """
    Class for individual preference storage and management
    """
    def __init__(self, value, rigidity: float = 0):
        self.value = value
        self.rigidity = rigidity #0 is a hard constraint, any positive float is how much flexibility there is. never goes below 0, max 1

    def get_preferences(self):
        retValue = self.value
        if isinstance(retValue, PurchaseType):
            retValue = retValue.value
        return {
            'value': retValue,
            'rigidity': self.rigidity
        }

    def update_user_preference(self, value):
        self.value = value

    def update_preference_rigidity(self, rigidity: float):
        self.rigidity = rigidity

    def print_preference(self):
        print(f"Value: {self.value}, Rigidity: {self.rigidity}")

    def return_flexibility(self):
        return self.rigidity


###TEST CASE###
if __name__ == '__main__':
    testCase = UserPreferences()
    testCase.update_constraint_value(Constraint.LOCATION, "Los Angeles")
    testCase.update_constraint_rigidity(Constraint.LOCATION, 0.5)

    testCase.update_constraint_value(Constraint.HOME_TYPE, "apartment")

    testCase.update_constraint_value(Constraint.BUDGET, 120000)

    testCase.update_constraint_value(Constraint.SQUARE_FEET, 1200)
    testCase.update_constraint_rigidity(Constraint.SQUARE_FEET, 0.1)

    try:
        testCase.update_constraint_value(Constraint.BUY_OR_RENT, "buy") #should fail, wrong type
    except ValueError:
        print("Test case success, wrong type handled correctly.")

    try:
        testCase.update_constraint_rigidity(Constraint.BUY_OR_RENT, 1) #should fail, always be 0
    except ValueError:
        print("Test case success, wrong rigidity handled correctly.")

    testCase.update_constraint_value(Constraint.BUY_OR_RENT, PurchaseType.RENT)

    testCase.update_constraint_value(Constraint.INCLUDE_NOT_FOR_SALE, True)


    testCase.print_constraints()
