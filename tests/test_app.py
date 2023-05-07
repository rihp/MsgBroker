import time
import json
from app import app, Channels

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_subscribe(client):
    response = client.post("/subscribe", json={"channel": "test_channel"})
    assert response.status_code == 200
    assert response.json["status"] == "Subscribed to test_channel"


def test_publish(client):
    response = client.post(
        "/publish", json={"channel": "test_channel", "message": "Hello"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "Message published"
from app import message_queues
import time

def test_fetch_messages(client):
    # Subscribe to a channel
    client.post('/subscribe', json={'channel': 'test_channel'})

    # Publish a message
    client.post('/publish', json={'channel': 'test_channel', 'message': 'Hello'})

    timeout = time.time() + 5  # 5 seconds from now
    messages_fetched = False

    while time.time() < timeout:
        # Check if there are any messages in the message_queues for the 'test_channel'
        if 'test_channel' in message_queues and not message_queues['test_channel'].empty():
            messages_fetched = True
            break

        time.sleep(0.5)  # Wait for 0.5 seconds before trying again

    assert messages_fetched, "Messages not fetched within the timeout period"



def test_subscribe_multiple_channels(client):
    channels = ["channel1", "channel2", "channel3"]
    for channel in channels:
        response = client.post("/subscribe", json={"channel": channel})
        assert response.status_code == 200
        assert response.json["status"] == f"Subscribed to {channel}"


def test_publish_multiple_channels(client):
    channels = ["channel1", "channel2", "channel3"]
    message = "Hello, world!"
    for channel in channels:
        response = client.post(
            "/publish", json={"channel": channel, "message": message}
        )
        assert response.status_code == 200
        assert response.json["status"] == "Message published"


def test_fetch_messages_multiple_channels(client):
    channels = ["channel1", "channel2", "channel3"]
    message = "Hello, world!"
    timeout = time.time() + 5  # 5 seconds from now

    # Subscribe to multiple channels and publish messages
    for channel in channels:
        client.post("/subscribe", json={"channel": channel})
        client.post("/publish", json={"channel": channel, "message": message})

    messages_fetched = {channel: False for channel in channels}

    while time.time() < timeout:
        for channel in channels:
            if (
                channel in message_queues
                and not message_queues[channel].empty()
                and not messages_fetched[channel]
            ):
                messages_fetched[channel] = True

        if all(messages_fetched.values()):
            break

        time.sleep(0.5)  # Wait for 0.5 seconds before trying again

    assert all(
        messages_fetched.values()
    ), "Messages not fetched within the timeout period for all channels"




def test_fetch_latest_message_from_each_channel(client):
    # Subscribe to all channels and publish a test message
    for channel in Channels:
        client.post("/subscribe", json={"channel": channel})
        client.post("/publish", json={"channel": channel, "message": f"Test message in {channel}"})

    # Fetch messages from all channels and check the latest message
    for channel in Channels:
        response = client.post("/fetch_messages", json={"channel": channel})
        assert response.status_code == 200

        data = json.loads(response.data)
        messages = data["messages"]

        assert len(messages) > 0
        latest_message = messages[-1]
        assert latest_message["channel"] == channel
        assert latest_message["message"] == f"Test message in {channel}"