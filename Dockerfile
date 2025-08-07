
FROM python:3.12-slim
#________________________#
WORKDIR /app
#________________________#
COPY . .
#________________________#
RUN pip install --no-cache-dir -r requirements.txt
#________________________#
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_ENV=development
#_______________________#
EXPOSE 5000
#_______________________#
CMD ["flask", "run"]