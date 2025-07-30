# python3-cyberfusion-rabbitmq-consumer-log-server

Log server for RabbitMQ consumer.

Use the [RabbitMQ consumer](https://github.com/CyberfusionIO/python3-cyberfusion-rabbitmq-consumer)?
The log server gives you an overview of RPC requests/responses - from all your RabbitMQ consumers - in one place.

![RPC requests overview](assets/rpc_requests_overview.png)

![RPC request detail](assets/rpc_request_detail.png)

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-rabbitmq-consumer-log-server

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

The log server consists of two parts: a web-based GUI, and an API.

## API

The RabbitMQ consumer writes RPC requests/responses to the API. To let the consumer ship logs to the log server, see the consumer's [README](https://github.com/CyberfusionIO/python3-cyberfusion-rabbitmq-consumer/blob/master/README.md#central-logging).

In the consumer, an API token must be set. Set it in `/etc/rabbitmq-consumer-log-server/api_token` (regular text file).

You can generate a random API token using `openssl`: `openssl rand -hex 32`

You don't need to keep the API token confidential: it's only used by the RabbitMQ consumer to **write** logs. Therefore, abuse would be a nuisance at the worst, not a data breach.

## GUI

Use the web-based GUI to view RPC requests/responses.

The web GUI uses basic authentication. Set a password in `/etc/rabbitmq-consumer-log-server/gui_password` (regular text file).

You can generate a random password using `openssl`: `openssl rand -hex 32`

You can use any basic authentication username - it's ignored.

## Retention

By default, logs are kept for 45 days. To override this, set the environment variable `KEEP_DAYS` to the number of days.

## Periodic tasks

Using the Debian package? You don't have to do anything - periodic tasks are automatically executed using cron.

Otherwise, run the following commands periodically:

* `rabbitmq-consumer-log-server-purge-logs` (every 24 hours)

# Usage

## Run

### Manually

* Run migrations: `alembic upgrade head`
* Run the app using an ASGI server such as Uvicorn.

### systemd

The server runs on `:::4194`.

    systemctl start rabbitmq-consumer-log-server.service

### Web GUI

Once the server is started, access the web GUI on `/rpc-requests`.

## SSL

Use a proxy that terminates SSL. E.g. [HAProxy](http://www.haproxy.org/).

When using a reverse proxy, `127.0.0.1` is *trusted* by default. To override this, set the `FORWARDED_ALLOW_IPS` environment variable.
For more information, see the [Uvicorn documentation](https://www.uvicorn.org/deployment/#running-from-the-command-line) (look for `--proxy-headers` and `--forwarded-allow-ips`).

## ⚠️ Development

Developing the RabbitMQ consumer? Access the API documentation on `/redoc` (Redoc) and `/docs` (Swagger).

Developing the log server? After installing it, and running migrations, seed your database with example data:

```bash
python3 seed_example_data.py
````

You can run the seeder multiple times to fill up your database with more data.
