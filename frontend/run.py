from dotenv import load_dotenv
load_dotenv()  # ← 起動前に環境変数を読み込む

from app import create_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
