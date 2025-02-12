FROM python:3.13
WORKDIR /usr/local/rocket_simulator

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8050

RUN useradd app && chown -R app /usr/local/rocket_simulator

ENV MPLCONFIGDIR=/home/rocket_simulator/.config/matplotlib
ENV DISKCACHE_DIRECTORY=/usr/local/rocket_simulator/cache

CMD [ "python", "WebApp/app.py" ]