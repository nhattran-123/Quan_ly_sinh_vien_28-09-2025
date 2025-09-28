from __init__ import create_app   # gọi từ __init__.py ở gốc dự án

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
