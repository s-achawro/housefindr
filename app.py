# # app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from constraints import Constraint 

# Your UTA.py must be in the same folder and define class UTAlgorithm

# ///Old
# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

import UTA
from constraints import Constraint

app = Flask(__name__)
CORS(app)

# --- Boot engine (UTA.py opens "houselisting.db" in CWD) ---
engine = UTA.UTAlgorithm()

# ---------- Helpers ----------
def listing_to_dict(h):
    if h is None:
        return None
    _id = str(getattr(h, "id", ""))
    base = {
        "id": str(getattr(h, "id", "")),
        "price": getattr(h, "price", None),
        "sqft": getattr(h, "sqft", None),
        "beds": getattr(h, "beds", None),
        "baths": getattr(h, "baths", None),
        "city": getattr(h, "city", None),
        "style": getattr(h, "style", None),
        "listing_type": getattr(h, "listing_type", None),
        "tenure": getattr(h, "tenure", None),
        "image_url": engine.idToImg.get(_id),
    }
    try:
        for k, v in getattr(h, "__dict__", {}).items():
            if k not in base:
                base[k] = v
    except Exception:
        pass
    return base

def try_fill_with_raw_db(target_len=2):
    # for visual fallback: , just first DB items
    while len(engine.feed) < target_len and len(engine.database) > 0:
        engine.feed.append(engine.database.pop(0))

def ensure_feed(target_len=2):
    # attempt a few times via recommender
    attempts = 0
    while len(engine.feed) < target_len and attempts < 3 and len(engine.database) > 0:
        engine.reccomend_2_homes()
        attempts += 1
    # fallback for UI to still shows something
    if len(engine.feed) < target_len:
        try_fill_with_raw_db(target_len=target_len)



# --- Constraints API ---
@app.get("/constraints")
def get_constraints():
    #UTA returns -> convert to JSONable
    prefs = engine.get_user_preferences()
    out = {
        "home_type": list(prefs.get("home_type", [])),
        "style": list(prefs.get("style", [])),
        "location": prefs.get("location"),
        "square_feet": prefs.get("square_feet"),
        "budget": prefs.get("budget"),
    }
    return jsonify(out)

@app.post("/constraints")
def set_constraints():
    data = request.get_json(force=True) or {}
    # Expecting: { home_type: [..], style: [..], location: str, square_feet: int, budget: int }
    if "home_type" in data:
        engine.update_constraint(Constraint.HOME_TYPE, set(map(str, data["home_type"])))
    if "style" in data:
        engine.update_constraint(Constraint.STYLE, set(map(str, data["style"])))
    if "location" in data:
        engine.update_constraint(Constraint.LOCATION, str(data["location"]))
    if "square_feet" in data:
        engine.update_constraint(Constraint.SQUARE_FEET, int(data["square_feet"]))
    if "budget" in data:
        engine.update_constraint(Constraint.BUDGET, int(data["budget"]))

    # Return the normalized preferences
    return get_constraints()

# ---------- Routes ----------
@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "database_len": len(getattr(engine, "database", [])),
        "feed_len": len(getattr(engine, "feed", [])),
    })

@app.get("/debug")
def debug():
    return jsonify({
        "db_exists": True,
        "database_len": len(getattr(engine, "database", [])),
        "feed_len": len(getattr(engine, "feed", [])),
        "listings_len": len(getattr(engine, "listings", [])) if hasattr(engine, "listings") else None
    })

# 1) raw first N items from DB (quick way to just show something)
@app.get("/first")
def first_from_db():
    try:
        n = int(request.args.get("count", "1"))
    except ValueError:
        n = 1
    n = max(0, n)
    db = getattr(engine, "database", [])
    out = [listing_to_dict(h) for h in db[:n]]
    return jsonify({"count": len(out), "items": out})

# 2) init: seed constraints + fill feed (GET)
@app.get("/init")
def init():
    # seed_reasonable_defaults()
    ensure_feed(target_len=2)
    current = engine.feed[0] if len(engine.feed) > 0 else None
    next_item = engine.feed[1] if len(engine.feed) > 1 else None
    return jsonify({
        "ok": True,
        "current": listing_to_dict(current),
        "next": listing_to_dict(next_item),
        "feed_preview": [listing_to_dict(x) for x in engine.feed[:6]],
        "feed_size": len(engine.feed),
        "database_remaining": len(engine.database),
    })

# 3) view feed (GET)
@app.get("/feed")
def feed():
    ensure_feed(target_len=2)
    current = engine.feed[0] if len(engine.feed) > 0 else None
    next_item = engine.feed[1] if len(engine.feed) > 1 else None
    return jsonify({
        "current": listing_to_dict(current),
        "next": listing_to_dict(next_item),
        "feed_preview": [listing_to_dict(x) for x in engine.feed[:6]],
        "feed_size": len(engine.feed),
        "database_remaining": len(engine.database),
    })

# 4) feedback to advance feed (POST)
@app.post("/feedback")
def feedback():
    data = request.get_json(force=True, silent=True) or {}
    listing_id = str(data.get("id", ""))
    liked = bool(data.get("liked", False))

    current = engine.feed[0] if len(engine.feed) > 0 else None
    if current is None or str(getattr(current, "id", "")) != listing_id:
        return jsonify({"ok": False, "error": "Current item does not match provided id."}), 400

    # update model
    engine.algorithm.update_user_feedback(engine.constraints, current, liked)

    # pop current & refill
    engine.feed.pop(0)
    ensure_feed(target_len=2)

    new_current = engine.feed[0] if len(engine.feed) > 0 else None
    new_next = engine.feed[1] if len(engine.feed) > 1 else None
    weights = getattr(engine.algorithm, "weights", None)
    weights_out = {k: round(v, 3) for k, v in weights.items()} if isinstance(weights, dict) else None

    return jsonify({
        "ok": True,
        "updated_weights_example": weights_out,
        "current": listing_to_dict(new_current),
        "next": listing_to_dict(new_next),
        "feed_size": len(engine.feed),
        "database_remaining": len(engine.database),
    })


# ---------- Main ----------
if __name__ == "__main__":
    #  auto-seed preferences:
    # seed_reasonable_defaults()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)

