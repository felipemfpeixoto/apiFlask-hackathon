from app import create_app
import os

host_ip = os.getenv("HOST_IP")
if not host_ip:
    raise ValueError("HOST_IP não definida no .env")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host=host_ip, port=5000)
