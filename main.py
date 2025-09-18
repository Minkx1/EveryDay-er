import flask
import json
import requests
import os
import base64
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = flask.Flask(__name__)

PLANS_FILE = "plans.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Minkx1/EveryDay-er/refs/heads/main/plans.json"
GITHUB_API_URL = "https://api.github.com/repos/Minkx1/EveryDay-er/contents/plans.json"
GITHUB_TOKEN = os.getenv("TOKEN")

def load_plans():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }
    r = requests.get(GITHUB_API_URL, headers=headers)
    if r.status_code == 200:
        return r.json() if "application/json" in r.headers.get("Content-Type", "") else r.json()
    return {}

def save_plans(plans):
    # Спочатку отримуємо SHA файлу
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(GITHUB_API_URL, headers=headers)
    if r.status_code != 200:
        print("Не вдалося отримати SHA файлу")
        return

    sha = r.json()["sha"]

    data = {
        "message": "Update plans.json via Flask",
        "content": base64.b64encode(json.dumps(plans, ensure_ascii=False, indent=4).encode()).decode(),
        "sha": sha
    }

    put_resp = requests.put(GITHUB_API_URL, headers=headers, json=data)
    if put_resp.status_code not in [200, 201]:
        print("Помилка при збереженні:", put_resp.text)

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
    app.run(debug=False, host="0.0.0.0", port="5000")