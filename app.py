from flask import Flask
 
# Create a Flask application instance

app = Flask(__name__)
 
# Define a route for the homepage

@app.route('/')

def hello_world():

    return 'Hello, World!'
 
# Run the application
@app.route('/')
def index():
    return "Welcome to the homepage!"

@app.route('/about')
def about():
    return "This is the about page." 

if __name__ == '__main__':

    app.run(debug=True)  # debug=True enables automatic reloader and debugger
 
    

