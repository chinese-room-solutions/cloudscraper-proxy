## Cloudscraper Proxy

![Python Version](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Codecov](https://codecov.io/gh/chinese-room-solutions/cloudscraper-proxy/branch/main/graph/badge.svg)

### What is this?

This is a simple proxy that uses [cloudscraper](https://github.com/venomous/cloudscraper) to bypass Cloudflare's anti-bot page.

### How to use?

* Run docker compose:
```
docker compose up -d
```
* Create a persistent agent (exists until the service is restarted or the agent is deleted):
```
curl -X POST localhost:5000/agent/persistent
```
* Use the agent:
```
curl -X GET "localhost:5000/proxy?agent_id=0&dst=https://example.com"
```
* Delete the agent:
```
curl -X DELETE localhost:5000/agent/persistent/0
```
* Generate a user agent and the `cf_clearance` cookie using the ephemeral agent:
```
curl -X POST "localhost:5000/agent/ephemeral?url=https://example.com"
```
* To make a request without explicitely creating an agent:
```
curl -b cookies.txt -c cookies.txt -X GET "localhost:5000/proxy?dst=https://example.com"
```
This will create a persistent agent and the `cloudscraper-agent-id` cookie will be set. You can use this cookie to make sequential requests with the same agent.
* To refresh and build the image again:
```
docker compose build --no-cache
```
* To remove the container:
```
docker compose down --remove-orphans
```
* OpenAPI documentation is available at the [/apispec](http://localhost:5000/apispec) endpoint.

### How to develop?

* Install [pyenv](https://github.com/pyenv/pyenv#installation)
* Install the desired Python >= 3.11: `pyenv install 3.12` 
* Create a virtualenv: `pyenv virtualenv 3.12 cloudscraper-proxy`
* Activate the virtualenv: `pyenv activate cloudscraper-proxy`
* Install the dependencies: `pip install -r requirements.txt`
* Run the proxy with built-in Flask server: `PYTHONPATH="${PYTHONPATH}:." python main.py`
* Run the proxy with Gunicorn: `PYTHONPATH="${PYTHONPATH}:."  gunicorn -b 0.0.0.0:5000 -c utils/gunicorn_config.py wsgi:app`
* Run the tests: `PYTHONPATH="${PYTHONPATH}:." coverage run -m unittest discover tests/`
* Deactivate the virtualenv: `pyenv deactivate`

If you're using VSCode, `launch.json` is included, so you can run development with F5.

**Development notes**

* Don't forget to update `__version__.py` when you make changes according to [semver](https://semver.org/).
* Update and run unit tests before pushing.
* For commit messages forllow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
