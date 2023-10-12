# PyAuthCXMLogin
PyAuthCXMLogin is a Python Authentication Client for Xbox Live Minecraft Login. It is a network library that implements the authentication scheme based on the [wiki.vg](https://wiki.vg/Microsoft_Authentication_Scheme) documentation. The need for this library arose because Mojang Auth has been deprecated, and this library provides a solution to obtain a valid authentication token for logging into Minecraft servers.

## Usage
Before you can effectively use this library, you must set up an Azure application and obtain the necessary credentials. Follow these [instructions](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) to create the Azure application.

Once you've registered your application, you'll receive the credentials needed for the `config.ini` file. In `config.ini`, fill in the following information under the [dev] section:
```
[dev]
client_id = 67****91-****-****-****-6d1****7101f # uuid
client_secret = .**_2_Z_o83****E.Ws.****UHgg6Z****  # url-safe string
redirect_uri = http://localhost:5000/getAToken #some nonexistent url 
```
### Default Method
You can use the default method in main.py to get prompted for your email and password to initiate the login process. Here's an example:
```
    python main.py
    Input Email: your_fakeemail@outlook.com
    Input Password: your_fakepassword               #Note: This is not visible with getpass for security reasons
    Tokens not detected ... Logging in with your_fakeemail@outlook.com
    ...
    Welcome back, Your_fakeplayer
```
### Advance methods
1. Alternatively, you can pass your email credentials to login to your connected Minecraft account programmatically. Like this:
```
    #In main.py
    login_data  = client.Login(email='your_fakeemail@outlook.com', password='your_fakepassword')
    login_data.authenticate()
```
2. You can also use refresh tokens. After the first successful login attempt, two files, `mc_client_token.txt` and `msft_refresh_token.txt`, will be generated. These tokens allow you to maintain your authentication session without the need to re-enter your credentials. You can delete or move these tokens if you wish to log into another player account.

## Requirements
To get started, ensure you have all the necessary dependencies. You can install them using the following command:
```
pip install -r requirements.txt
```
Please note that this library is not designed to handle accounts with Two-Factor Authentication (2FA) enabled.

## Setup Virtual Environment
In the console or terminal, type `python -m venv venv` to initialize the python virtual environment. In linux, you might have to run `sudo apt update && apt update -y` to install pip for later uses.
```
# Windows Users
.\venv\Scripts\activate

# Unix/ Mac Users
source venv/bin/activate

# Exit venv Command
deactivate

```

## License
This project is licensed under the GNU General Public License, Version 3 (GNU v3 License). You are welcome to use this library in your projects. If you choose to utilize this code, please consider referencing this project in your work. Thank you!