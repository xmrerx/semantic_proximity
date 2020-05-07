FROM python:3
COPY . /app
WORKDIR /app 
RUN pip3 install -r requirements.txt
RUN python3 -m spacy download en
RUN python3 -m nltk.downloader punkt
# CMD [ "python3", "app.py" ]