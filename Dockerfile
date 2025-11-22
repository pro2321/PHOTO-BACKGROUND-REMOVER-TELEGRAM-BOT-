FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

# এখানে লক্ষ্য করুন: "main:server" এর বদলে "main:asgi_app" দেওয়া হয়েছে
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000", "main:asgi_app"]
