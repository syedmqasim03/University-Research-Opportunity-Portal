
import os
from datetime import date

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3307")),
        user=os.getenv("MYSQL_USER", "research_app"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "research_portal"),
    )


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


def validate_opportunity(data, is_update=False):
    required_fields = [
        "title",
        "description",
        "research_area",
        "faculty_name",
        "department",
        "required_skills",
        "available_positions",
        "application_deadline",
    ]

    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    for field in required_fields:
        if field not in data and not is_update:
            return f"Missing required field: {field}"

    for field in required_fields:
        if field in data:
            value = data[field]

            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                return f"{field} cannot be empty."

    if "available_positions" in data:
        positions = data["available_positions"]

        if (
            isinstance(positions, bool)
            or not isinstance(positions, int)
            or positions < 1
        ):
            return "available_positions must be a positive integer."

    if "application_deadline" in data:
        try:
            date.fromisoformat(data["application_deadline"])
        except (ValueError, TypeError):
            return "application_deadline must use YYYY-MM-DD format."

    if "status" in data and data["status"] not in ["Open", "Closed"]:
        return "status must be Open or Closed."

    return None


def opportunity_from_row(row):
    row["application_deadline"] = row["application_deadline"].isoformat()
    return row


@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    data = request.get_json(silent=True)
    if data is None:
        return error_response("A valid JSON request body is required.", 400)

    error = validate_opportunity(data)
    if error:
        return error_response(error, 400)

    fields = [
        "title", "description", "research_area", "faculty_name",
        "department", "required_skills", "available_positions",
        "application_deadline",
    ]

    values = [data[field] for field in fields]
    status = data.get("status", "Open")

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        sql = """
            INSERT INTO research_opportunities
            (title, description, research_area, faculty_name, department,
             required_skills, available_positions, application_deadline, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, values + [status])
        connection.commit()

        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT * FROM research_opportunities WHERE id = %s",
            (new_id,),
        )
        result = opportunity_from_row(cursor.fetchone())

        return jsonify(result), 201

    except mysql.connector.Error:
        app.logger.exception("Database error while creating opportunity")
        return error_response("A database error occurred.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/opportunities", methods=["GET"])
def get_opportunities():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM research_opportunities ORDER BY id")
        rows = cursor.fetchall()

        return jsonify([opportunity_from_row(row) for row in rows]), 200
    except mysql.connector.Error:
        app.logger.exception("Database error while listing opportunities")
        return error_response("A database error occurred.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["GET"])
def get_opportunity(opportunity_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM research_opportunities WHERE id = %s",
            (opportunity_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return error_response("Opportunity not found.", 404)

        return jsonify(opportunity_from_row(row)), 200
    except mysql.connector.Error:
        app.logger.exception("Database error while retrieving opportunity")
        return error_response("A database error occurred.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["PUT"])
def update_opportunity(opportunity_id):
    data = request.get_json(silent=True)
    if data is None:
        return error_response("A valid JSON request body is required.", 400)

    allowed_fields = {
        "title", "description", "research_area", "faculty_name",
        "department", "required_skills", "available_positions",
        "application_deadline", "status",
    }

    if not isinstance(data, dict):
        return error_response("Request body must be a JSON object.", 400)

    if not data:
        return error_response("Provide at least one field to update.", 400)

    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        return error_response(
            "Unknown field(s): " + ", ".join(sorted(unknown_fields)), 400
        )

    error = validate_opportunity(data, is_update=True)
    if error:
        return error_response(error, 400)

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM research_opportunities WHERE id = %s",
            (opportunity_id,),
        )
        existing = cursor.fetchone()

        if existing is None:
            return error_response("Opportunity not found.", 404)

        assignments = ", ".join(f"{field} = %s" for field in data)
        values = list(data.values()) + [opportunity_id]

        cursor.execute(
            f"UPDATE research_opportunities SET {assignments} WHERE id = %s",
            values,
        )
        connection.commit()

        cursor.execute(
            "SELECT * FROM research_opportunities WHERE id = %s",
            (opportunity_id,),
        )
        result = opportunity_from_row(cursor.fetchone())

        return jsonify(result), 200
    except mysql.connector.Error:
        app.logger.exception("Database error while updating opportunity")
        return error_response("A database error occurred.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM research_opportunities WHERE id = %s",
            (opportunity_id,),
        )
        connection.commit()

        if cursor.rowcount == 0:
            return error_response("Opportunity not found.", 404)

        return jsonify({"message": "Opportunity deleted successfully."}), 200
    except mysql.connector.Error:
        app.logger.exception("Database error while deleting opportunity")
        return error_response("A database error occurred.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)