import json
import os

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from ai_service import AIRefusalError, AIServiceUnavailableError, extract_project

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)


SEED_AUTHOR_NAME = "Backling Karikari"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    projects = db.relationship("Project", backref="author")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default="")
    summary = db.Column(db.Text, nullable=False, default="")
    technologies = db.Column(db.Text, nullable=False, default="")
    likes = db.Column(db.Integer, nullable=False, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "summary": self.summary,
            "technologies": self.technologies,
            "likes": self.likes,
            "author": self.author.name,
        }


def init_seed_data():
    if db.session.query(Project.id).first() is not None:
        return

    seed_path = os.path.join(app.root_path, "projects_seed.json")
    with open(seed_path, encoding="utf-8") as seed_file:
        seed_projects = json.load(seed_file)

    author = Author(name=SEED_AUTHOR_NAME)
    projects = [
        Project(
            id=project["id"],
            title=project["title"],
            description=project.get("description", ""),
            summary=project.get("description", ""),
            likes=project.get("likes", 0),
            author=author,
        )
        for project in seed_projects
    ]
    db.session.add(author)
    db.session.add_all(projects)
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

    normalized_title = title.strip()
    if Project.query.filter_by(title=normalized_title).first() is not None:
        return jsonify({"error": "A project with this title already exists"}), 400

    author = Author.query.filter_by(name=SEED_AUTHOR_NAME).first()
    if author is None:
        app.logger.error("Seed author %r is missing", SEED_AUTHOR_NAME)
        return jsonify({"error": "The project could not be saved"}), 500

    project = Project(title=normalized_title, author=author)
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to create project")
        return jsonify({"error": "The project could not be saved"}), 400

    return jsonify(project.to_dict()), 201


@app.route("/api/projects/smart", methods=["POST"])
def smart_create_project():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Project notes are required"}), 400

    notes = data.get("notes")
    if not isinstance(notes, str) or len(notes.strip()) < 20:
        return jsonify({"error": "Notes must be at least 20 characters"}), 400

    author = Author.query.filter_by(name=SEED_AUTHOR_NAME).first()
    if author is None:
        app.logger.error("Seed author %r is missing", SEED_AUTHOR_NAME)
        return jsonify({"error": "The project could not be saved"}), 500

    try:
        extracted = extract_project(notes.strip())
    except AIRefusalError:
        return jsonify({"error": "The project notes could not be processed"}), 422
    except AIServiceUnavailableError:
        app.logger.error("The AI provider is unavailable")
        return jsonify({"error": "The AI provider is unavailable"}), 503

    title = extracted.title.strip()
    summary = extracted.summary.strip()
    technologies = ", ".join(
        technology.strip()
        for technology in extracted.technologies
        if technology.strip()
    )
    if not title or not summary or not technologies:
        return jsonify({"error": "The AI provider returned incomplete project details"}), 502

    project = Project(
        title=title,
        description=summary,
        summary=summary,
        technologies=technologies,
        author=author,
    )
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to create project from notes")
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
