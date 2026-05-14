
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import psycopg

app = Flask(__name__)
DB_URL = os.getenv("DB_URL")

def db():
    return psycopg.connect(DB_URL, autocommit=True)

def init_db():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS players ("
            "id SERIAL PRIMARY KEY,"
            "name TEXT UNIQUE NOT NULL,"
            "created_at TIMESTAMPTZ NOT NULL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS matches ("
            "id SERIAL PRIMARY KEY,"
            "played_at TIMESTAMPTZ NOT NULL,"
            "x_player_id INTEGER REFERENCES players(id),"
            "o_player_id INTEGER REFERENCES players(id),"
            "winner TEXT CHECK (winner IN ('X','O','DRAW')))"
        )

def upsert_player(conn, name):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM players WHERE name=%s", (name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO players (name, created_at) VALUES (%s,%s) RETURNING id",
            (name, datetime.utcnow())
        )
        return cur.fetchone()[0]

def rows(cur):
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/leaderboard")
def leaderboard():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT p.name,"
            "COALESCE(SUM(CASE "
            "WHEN m.winner='X' AND m.x_player_id=p.id THEN 1 "
            "WHEN m.winner='O' AND m.o_player_id=p.id THEN 1 "
            "ELSE 0 END),0) AS wins,"
            "COALESCE(SUM(CASE WHEN m.winner='DRAW' THEN 1 ELSE 0 END),0) AS draws,"
            "COUNT(m.id) AS games "
            "FROM players p "
            "LEFT JOIN matches m ON m.x_player_id=p.id OR m.o_player_id=p.id "
            "GROUP BY p.id "
            "ORDER BY wins DESC"
        )
        return jsonify(rows(cur))

@app.post("/api/match")
def match():
    d = request.get_json()
    with db() as conn:
        x = upsert_player(conn, d["x_player"])
        o = upsert_player(conn, d["o_player"])
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO matches (played_at,x_player_id,o_player_id,winner) "
                "VALUES (%s,%s,%s,%s)",
                (datetime.utcnow(), x, o, d["winner"])
            )
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
