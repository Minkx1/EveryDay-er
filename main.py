import flask
import json
from datetime import datetime

app = flask.Flask(__name__)

PLANS_FILE = "plans.json"

def load_plans():
    try:
        with open(PLANS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_plans(plans):
    with open(PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=4)

# ===== HOME =====
@app.route("/")
def home():
    plans = load_plans()
    current_date = datetime.now().strftime("%d.%m.%Y")

    week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    week_plans = {d: plans.get(d, []) for d in week_days}
    date_plans = {d: events for d, events in plans.items() if d not in week_days and d != "data"}

    return flask.render_template(
        "home.html",
        week_plans=week_plans,
        date_plans=date_plans,
        current_date=current_date
    )

# ===== ADD DAY =====
@app.route("/add_day", methods=["POST"])
def add_day():
    date = flask.request.form.get("date")
    if not date:
        return flask.redirect("/")
    plans = load_plans()
    if date not in plans:
        plans[date] = []
        save_plans(plans)
    return flask.redirect("/")

# ===== DELETE DAY =====
@app.route("/delete_day", methods=["POST"])
def delete_day():
    day = flask.request.form.get("day")
    if not day:
        return flask.redirect("/")
    plans = load_plans()
    if day in plans:
        plans.pop(day)
        save_plans(plans)
    return flask.redirect("/")

# ===== ADD EVENT =====
@app.route("/add_event", methods=["POST"])
def add_event():
    day = flask.request.form.get("day")
    name = flask.request.form.get("name")
    time = flask.request.form.get("time")
    if not (day and name and time):
        return flask.redirect("/")
    plans = load_plans()
    if day not in plans:
        plans[day] = []
    plans[day].append({"name": name, "time": time})
    save_plans(plans)
    return flask.redirect("/")

# ===== EDIT EVENT =====
@app.route("/edit_event", methods=["POST"])
def edit_event():
    day = flask.request.form.get("day")
    index = int(flask.request.form.get("index", -1))
    name = flask.request.form.get("name")
    time = flask.request.form.get("time")
    plans = load_plans()
    if day in plans and 0 <= index < len(plans[day]):
        plans[day][index] = {"name": name, "time": time}
        save_plans(plans)
    return flask.redirect("/")

# ===== ВИДАЛИТИ ПОДІЮ =====
@app.route("/delete_event", methods=["POST"])
def delete_event():
    day = flask.request.form.get("day")
    index = int(flask.request.form.get("index", -1))
    plans = load_plans()
    if day in plans and 0 <= index < len(plans[day]):
        plans[day].pop(index)
        save_plans(plans)
    return flask.redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")