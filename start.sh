
export FLASK_APP=main.py  
export FLASK_DEBUG=1 
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8200

pkill -9 python3
pkill -9 celery

[ ! -d ./log ] && mkdir log

nohup  flask run  --host ${FLASK_HOST} --port  ${FLASK_PORT} >>log/run.log 2>&1  &

nohup celery -A worker.celery worker -Q celery >>log/celery.log 2>&1  &


