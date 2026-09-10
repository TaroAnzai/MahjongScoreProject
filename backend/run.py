from environment import load_environment

load_environment()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
