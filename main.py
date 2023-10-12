import sys
from CXMLogin import login as client

def main():
    #Get Player Login Info
    login_data  = client.Login()
    login_data.authenticate()
    try:
        if login_data.get_status():
            print("Welcome back, "+ login_data.get_username())
        else:
            raise ValueError("Login failed ...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()