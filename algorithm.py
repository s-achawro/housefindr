from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import math

# ---------- Data model ----------
@dataclass
class Listing:
    id: str
    price: int
    sqft: int
    beds: int
    baths: float
    city: str
    listing_type: str        # "single", "family", "condo", etc.
    tenure: str              # "buy" or "rent"
    is_sold: bool = False

# ---------- Recommender ----------
class HousingRecommender:
    def __init__(self, constraints: Dict[str, Any]):
        """
        constraints keys (all optional):
            city (set[str] or str), max_price (int), min_sqft (int),
            listing_type (set[str] or str), tenure (str), include_sold (bool)
        """
        self.constraints = constraints
        # User preference vector (higher = better). Start neutral.
        # Normalize features internally when scoring.
        self.weights = {
            "price": -0.6,     # cheaper better (negative weight)
            "sqft": 0.6,
            "beds": 0.3,
            "baths": 0.3,
            "city": 0.4,       # categorical match bonus
            "listing_type": 0.2,
            "tenure": 0.6
        }
        self.lr = 0.1  # learning rate for feedback updates

    # ---- Filtering by hard constraints ----
    def _passes_constraints(self, h: Listing) -> bool:
        c = self.constraints
        if not c.get("include_sold", False) and h.is_sold:
            return False
        if "tenure" in c and c["tenure"] and h.tenure != c["tenure"]:
            return False
        if "max_price" in c and c["max_price"] and h.price > c["max_price"]:
            return False
        if "min_sqft" in c and c["min_sqft"] and h.sqft < c["min_sqft"]:
            return False
        if "listing_type" in c and c["listing_type"]:
            allowed = c["listing_type"]
            if isinstance(allowed, str):
                allowed = {allowed}
            if h.listing_type not in allowed:
                return False
        if "city" in c and c["city"]:
            allowed = c["city"]
            if isinstance(allowed, str):
                allowed = {allowed}
            if h.city not in allowed:
                return False
        return True

    # ---- Normalizers (min-max on-the-fly from candidate pool) ----
    def _build_norms(self, listings: List[Listing]):
        vals = lambda key: [getattr(x, key) for x in listings] or [0]
        def mm(v):
            lo, hi = min(v), max(v)
            return (lo, hi if hi != lo else lo + 1)
        self._norm = {
            "price": mm(vals("price")),
            "sqft":  mm(vals("sqft")),
            "beds":  mm(vals("beds")),
            "baths": mm(vals("baths")),
        }

    def _norm_val(self, key: str, v: float) -> float:
        lo, hi = self._norm[key]
        return (v - lo) / (hi - lo)

    # ---- Scoring ----
    def _score(self, h: Listing) -> float:
        # numeric components
        price_n = self._norm_val("price", h.price)      # higher = more expensive
        sqft_n  = self._norm_val("sqft",  h.sqft)
        beds_n  = self._norm_val("beds",  h.beds)
        baths_n = self._norm_val("baths", h.baths)

        s = 0.0
        s += self.weights["price"] * price_n
        s += self.weights["sqft"]  * sqft_n
        s += self.weights["beds"]  * beds_n
        s += self.weights["baths"] * baths_n

        # categorical matches vs constraints (1 if matches preferred set, else 0)
        def match(val, pref):
            if not pref: return 0.0
            if isinstance(pref, str): pref = {pref}
            return 1.0 if val in pref else 0.0

        s += self.weights["city"]         * match(h.city, self.constraints.get("city"))
        s += self.weights["listing_type"] * match(h.listing_type, self.constraints.get("listing_type"))
        s += self.weights["tenure"]       * match(h.tenure, self.constraints.get("tenure"))
        return s

    # ---- Public API ----
    def recommend(self, listings: List[Listing], top_k: Optional[int] = None) -> List[Listing]:
        pool = [h for h in listings if self._passes_constraints(h)]
        if not pool:
            return []
        self._build_norms(pool)
        scored = [(self._score(h), h) for h in pool]
        scored.sort(reverse=True, key=lambda x: x[0])
        ranked = [h for _, h in scored]
        return ranked[:top_k] if top_k else ranked

    def feedback(self, listing: Listing, liked: bool):
        """
        Simple online update: move weights toward features of liked homes,
        away from features of disliked homes.
        """
        # Build a pseudo-feature vector (normalized numeric + categorical matches)
        price_n = self._norm_val("price", listing.price)
        sqft_n  = self._norm_val("sqft",  listing.sqft)
        beds_n  = self._norm_val("beds",  listing.beds)
        baths_n = self._norm_val("baths", listing.baths)

        feats = {
            "price": price_n,
            "sqft":  sqft_n,
            "beds":  beds_n,
            "baths": baths_n,
            "city":  1.0,
            "listing_type": 1.0,
            "tenure": 1.0
        }
        direction = 1.0 if liked else -1.0
        for k in self.weights:
            # gradient-ascent style bump; clamp to reasonable range
            self.weights[k] += self.lr * direction * feats[k]
            self.weights[k] = max(-1.5, min(1.5, self.weights[k]))

# ---------- Example usage ----------
if __name__ == "__main__":
    listings = [
        Listing("A", price=750000, sqft=1200, beds=3, baths=2, city="Seattle", listing_type="single", tenure="buy"),
        Listing("B", price=2600,    sqft=900,  beds=2, baths=1, city="Seattle", listing_type="condo",  tenure="rent"),
        Listing("C", price=540000, sqft=1500, beds=4, baths=2, city="Redmond", listing_type="family", tenure="buy"),
        Listing("D", price=480000, sqft=1000, beds=2, baths=1, city="Bellevue", listing_type="condo",  tenure="buy", is_sold=True),
    ]

    constraints = {
        "city": {"Seattle", "Redmond"},
        "max_price": 800000,
        "min_sqft": 900,
        "listing_type": {"single", "condo", "family"},
        "tenure": "buy",
        "include_sold": False
    }

    rec = HousingRecommender(constraints)
    ranked = rec.recommend(listings)
    print("Initial ranking:", [h.id for h in ranked])

    # User swipes right on C, left on A; update and re-rank
    rec.feedback(next(h for h in listings if h.id == "C"), liked=True)
    rec.feedback(next(h for h in listings if h.id == "A"), liked=False)
    reranked = rec.recommend(listings)
    print("After feedback:", [h.id for h in reranked])