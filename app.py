import queue
import threading

from flask import Flask, jsonify, render_template, request
from redis import Redis
import enum


app = Flask(__name__)
redis_conn = Redis()

message_queues = {}


class Channels(enum.StrEnum):
    COMMANDS = "commands"
    ALL = "all"
    PROGRESS = "progress"
    MEMORIES = "memories"
    USER_INPUTS = "user_inputs"
    OBJECTIVES_PROMPTS = "objectives_prompts"
    AI_INPUTS = "ai_inputs"
    OUTPUTS = "outputs"

import json
def listen_to_channel(channel_name: Channels):
    pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(channel_name)

    message_queues[channel_name] = queue.Queue()

    while True:
        message = pubsub.get_message()
        if message:
            print(f"Received message on {channel_name}: {message['data']}")
            message_data = {"channel": channel_name, "data": message["data"]}
            message_queues[channel_name].put(message_data)

            # Republish the message in the "outputs" channel
            output_message_data = {
                "original_channel": str(channel_name),
                "message": message["data"].decode("utf-8"),
            }
            output_message_json = json.dumps(output_message_data)
            redis_conn.publish(Channels.OUTPUTS, output_message_json)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    channel_name = data["channel"]
    message = data["message"]
    redis_conn.publish(channel_name, message)

    print(f"Published message: {message} to channel: {channel_name}")  # Add this line


    return jsonify({"status": "Message published"})



@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json
    channel_name = data["channel"]

    listener_thread = threading.Thread(
        target=listen_to_channel, args=(channel_name,), daemon=True
    )
    listener_thread.start()

    return jsonify({"status": f"Subscribed to {channel_name}"})



@app.route("/fetch_messages", methods=["POST"])
def fetch_messages():
    data = request.json
    channel_name = data["channel"]

    if channel_name not in message_queues:
        return jsonify({"status": "Channel not found", "messages": []})

    messages = []
    while not message_queues[channel_name].empty():
        messages.append(message_queues[channel_name].get())


    message_list = [
        {"id": i, "channel": m["channel"], "message": m["data"].decode()}
        for i, m in enumerate(messages, start=0)
    ]

    return jsonify({"status": "Messages fetched", "messages": message_list})




if __name__ == "__main__":
    app.run(debug=True)
