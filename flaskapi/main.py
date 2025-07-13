from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='169.254.47.39', port=5000)
