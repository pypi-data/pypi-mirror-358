# BGP Collector

The **BGP Collector** is a Python service designed to receive BGP update messages from [ExaBGP](https://github.com/Exa-Networks/exabgp), process them, and store the extracted data in a PostgreSQL/TimescaleDB database. It uses Redis for session caching and RabbitMQ to buffer messages to prevent data loss during high-frequency BGP events.

---

## Features

- Receives and parses BGP updates from ExaBGP
- Uses Redis for caching session data
- Uses RabbitMQ as a message broker for resilience
- Stores data in TimescaleDB using time-series hypertables
- Supports concurrent processing with multiple workers

---
