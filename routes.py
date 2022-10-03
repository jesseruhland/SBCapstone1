




















@app.route("/facilities/<int:facility_pk>/comments/<int:comment_id>", methods=["GET", "PATCH", "DELETE"])

@app.route("/facilities/<int:facility_pk>/favorite", method=["POST"])