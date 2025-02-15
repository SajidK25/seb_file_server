from app import create_app

# Initialize the Flask application using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the app in development mode
    # Use `gunicorn` for running in production
    app.run(host="0.0.0.0", port=5000, debug=True)