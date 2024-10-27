from flask import Flask, request, jsonify, redirect
import random

app = Flask(__name__)
MAX_LEN = 7

@app.route("/longurl", methods=["POST"])
def shorten_url():
    data = request.json
    long_url = data.get("url")
    short_url = create_short_url()
    # while shortened url in DB: short_url = create_short_url()
    short_url = "http://"+get_current_host()+"/short/"+short_url
    # store long_url, short_url to DB
    return jsonify({"shortenedUrl": short_url})

def create_short_url():
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    length = random.choice(range(1,MAX_LEN+1))
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url
    
def get_current_host():
    try:
        host = request.host
        # port = request.environ.get('SERVER_PORT')
        # return f"{host}:{port}"
        return f"{host}"
    except Exception as e:
        print("Error:", e)
        return None


@app.route("/short/<short_url>", methods=["GET"])
def get_short_url(short_url):
    # Get long_url from short_url
    long_url = get_long_url(short_url)
    # Redirect to long_url
    print("short_url", short_url, "long_url", long_url)
    return redirect(long_url)

def get_long_url(short_url):
    # Placeholder logic to retrieve long URL from short URL from DB
    return "https://youtube.com/"

if __name__=="__main__":
    app.run(debug=True)