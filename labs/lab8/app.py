import json
import os

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default="")
    likes = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "likes": self.likes,
        }


def init_seed_data():
    if db.session.query(Project.id).first() is not None:
        return

    seed_path = os.path.join(app.root_path, "projects_seed.json")
    with open(seed_path, encoding="utf-8") as seed_file:
        seed_projects = json.load(seed_file)

    db.session.add_all(
        Project(
            id=project["id"],
            title=project["title"],
            description=project.get("description", ""),
            likes=project.get("likes", 0),
        )
        for project in seed_projects
    )
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


with app.app_context():
    db.create_all()
    init_seed_data()


@app.route("/")
def index():
    projects = Project.query.order_by(Project.id).all()
    return render_template(
        "index.html",
        projects=[project.to_dict() for project in projects],
    )


@app.route("/api/projects", methods=["GET"])
def list_projects():
    projects = Project.query.order_by(Project.id).all()
    return jsonify([project.to_dict() for project in projects])


@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A project title is required"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A project title is required"}), 400

    project = Project(title=title.strip())
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to create project")
        return jsonify({"error": "The project could not be saved"}), 400

    return jsonify(project.to_dict()), 201


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(app.root_path, "assets"), filename)


@app.route("/api/projects/<int:project_id>/upvote", methods=["POST"])
def upvote_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project.likes += 1
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to upvote project")
        return jsonify({"error": "The project could not be updated"}), 400

    return jsonify({"likes": project.likes})


if __name__ == "__main__":
    app.run(debug=True)
