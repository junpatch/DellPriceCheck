from . import create_app

app = create_app(config_name="development") # production / development / testing

if __name__ == "__main__":
    app.run()