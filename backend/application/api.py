from app import app
@app.route("/")
def home():
    return "Hello, World!"

@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json()
    login = data.get("login")
    pwd = data.get("password")
    return {message: "Login successful!", token: "abc123"}