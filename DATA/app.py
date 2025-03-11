from flask import Flask, request, render_template
import pymysql

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        season = request.form["season"]
        connection = pymysql.connect(host="localhost", user="root", password="", db="football_db")
        cursor = connection.cursor()
        query = """
            SELECT p.Name, ps.Goals 
            FROM Players p 
            JOIN PlayerSeasons ps ON p.PlayerID = ps.PlayerID 
            JOIN Seasons s ON ps.SeasonID = s.SeasonID 
            WHERE s.Year = %s 
            ORDER BY ps.Goals DESC 
            LIMIT 1
        """
        cursor.execute(query, (season,))
        data = cursor.fetchone()
        if data:
            result = {"name": data[0], "goals": data[1]}
        connection.close()
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)