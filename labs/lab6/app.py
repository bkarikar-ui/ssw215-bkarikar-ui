from flask import Flask, render_template

app = Flask(__name__)

projects_db = [
    {
        "id": 1,
        "title": "Robot navigation",
        "description": "Built an Arduino-based robot that uses A* pathfinding to navigate a grid.",
        "likes": 0,
    },
    {
        "id": 2,
        "title": "Smart watering system",
        "description": "Designed a smart watering system using sensors to monitor plants.",
        "likes": 0,
    },
    {
        "id": 3,
        "title": "My Tools",
        "description": "Want to make useful software tools that help college students stay organized.",
        "likes": 0,
    },
    {
        "id": 4,
        "title": "Web Scraper",
        "description": "Created a web scraper to extract data from multiple websites.",
        "likes": 0,
    },
]


@app.route("/")
def index():
    return render_template("index.html", projects=projects_db)


if __name__ == "__main__":
    app.run(debug=True)
