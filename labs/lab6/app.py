import os

from flask import Flask, jsonify, render_template, send_from_directory

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


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(app.root_path, "assets"), filename)


@app.route("/api/projects/<int:project_id>/upvote", methods=["POST"])
def upvote_project(project_id):
    project = next(
        (project for project in projects_db if project["id"] == project_id),
        None,
    )
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    return jsonify({"likes": project["likes"]})


if __name__ == "__main__":
    app.run(debug=True)
