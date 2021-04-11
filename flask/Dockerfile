# Use python image
FROM python:3.7.2-stretch
# Set working directory to 
WORKDIR /website
# COPY te current directory contents into the container at /website
ADD . /website
# install dependencies
RUN pip install -r requirements.txt
# Run the command to start uWSGI
CMD ["uwsgi", "app.ini"]
