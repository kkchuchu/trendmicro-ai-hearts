# Use an official Python runtime as a parent image
FROM tensorflow/tensorflow:latest-py3
 
# Set the working directory to /app
WORKDIR /app
 
# Copy the current directory contents into the container at /app
ADD . /app
 
# Install basic dependencies
RUN pip install -r requirements.txt

# Run sample_bot.py when the container launches, you should replace it with your program
# The parameters of the program should be "[player_name] [player_number] [token] [connect_url]"
ENTRYPOINT ["python", "src/sample_bot.py"]
