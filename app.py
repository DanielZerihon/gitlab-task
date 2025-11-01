from flask import Flask, request, jsonify
from gitlab_api import set_user_role, get_gitlab_data

app = Flask(__name__)

@app.route("/set-role", methods=["POST"])
def route_set_role():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        username = data.get("username")
        repo_or_group = data.get("repo_or_group")
        role = data.get("role")

        if not all([username, repo_or_group, role]):
            return jsonify({"error": "username, repo_or_group, and role are required"}), 400

        result, status = set_user_role(username, repo_or_group, role)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/get-data", methods=["GET"])
def get_data():
    try:
        data_type = request.args.get("type")
        year = request.args.get("year")

        if not data_type or not year:
            return jsonify({"error": "type and year parameters are required"}), 400

        result, status = get_gitlab_data(data_type, int(year))
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
