from werkzeug.security import generate_password_hash

def main():
    password = input("管理者パスワードを入力してください: ").strip()
    if not password:
        print("パスワードが空です。再実行してください。")
        return

    hashed = generate_password_hash(password, method="pbkdf2:sha256")
    print("\n=== パスワードハッシュ値 ===")
    print(hashed)
    print("\n※ この値を .env の ADMIN_PASSWORD_HASH に保存してください。")

if __name__ == "__main__":
    main()
