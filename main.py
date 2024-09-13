from flask import Flask, request

app = Flask(__name__)

# Define a route for the homepage
@app.route('/', methods=["POST"])
def home():
    print(request.data)
    return "Hello, Flask is running!"

if __name__ == '__main__':
    app.run(debug=True)
