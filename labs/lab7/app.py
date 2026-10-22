import json
import os

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

PROJECTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects.json")


def load_projects():
    with open(PROJECTS_FILE, encoding="utf-8") as project_file:
        return json.load(project_file)


def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as project_file:
        json.dump(projects, project_file, indent=2)


@app.route("/")
def index():
    return render_template("index.html", projects=load_projects())


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(app.root_path, "assets"), filename)


@app.route("/api/projects/<int:project_id>/upvote", methods=["POST"])
def upvote_project(project_id):
    projects = load_projects()
    project = next(
        (project for project in projects if project["id"] == project_id),
        None,
    )
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    save_projects(projects)
    return jsonify({"likes": project["likes"]})


if __name__ == "__main__":
    app.run(debug=True)
