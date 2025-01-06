FROM python:3.9
WORKDIR /usr/src/app
COPY ./src ./
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p logs
CMD [ "python", "./metric.py" ]
