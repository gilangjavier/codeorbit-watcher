# 🌍 CodeOrbit - Watcher

CodeOrbit - Watcher is a Discord bot that monitors the status of specified services and notifies users about their status. The bot sends notifications when services go down and when they come back up.

## Features

- Monitor the status of multiple web services.
- Notify on Discord when a service goes down.
- Notify on Discord when a service comes back up.
- Display service status information including response time and description.

## Requirements

- Python 3.8 or newer
- Pip (Python package installer)
- Docker (optional)

## Installation

1. Clone this repository

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # For Unix or MacOS
    .\venv\Scripts\activate  # For Windows
    ```

3. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project directory and add your environment variables:

    ```dotenv
    DISCORD_TOKEN=your_discord_bot_token
    NOTIFICATION_INTERVAL=5  # Notification interval in minutes
    TIMEOUT=60  # Timeout for HTTP requests in seconds
    ```

5. Create a `services.yaml` file in the project directory and add the services you want to monitor:

    ```yaml
    services:
      Frontend: https://example.com
      Backend: https://example.com/backend
      Payment: https://example.com/payment
    ```

## Usage

1. Run the bot with the following command:

    ```sh
    python bot.py
    ```

2. Once the bot is running, you can use the following commands in your Discord server:

    - `/check_status`:
      Checks the status of all services and displays the information in an embed message.

    - `/notification active`:
      Activates periodic notifications about the status of the services.

    - `/notification disable`:
      Disables periodic notifications about the status of the services.

## Create a docker-compose.yml file in the project directory:

```yaml
version: '3.8'

services:
  discord-bot:
    build: .
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - NOTIFICATION_INTERVAL=${NOTIFICATION_INTERVAL}
      - TIMEOUT=${TIMEOUT}
    volumes:
      - .:/app
```
## Create a Dockerfile in the project directory:

```Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

## Run Docker Compose:

```sh
docker-compose up -d
```

This will build and run the bot in a Docker container.

## Contribution
Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License.
