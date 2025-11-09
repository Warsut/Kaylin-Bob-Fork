#base image
FROM python:3.9-slim

#set the working directory in the container, create app folder in container
WORKDIR /app 

#copy the current directory contents into the container 
COPY . /app

#install the required dependencies
RUN pip install -r requirements.txt

#command to run, server port # (8501) is for streamlit
CMD ["streamlit", "run", "Bob.py", "--server.port=8501", "--server.address=0.0.0.0"]
