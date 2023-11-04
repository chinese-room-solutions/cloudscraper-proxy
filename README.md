## Cloudscraper Proxy

### What is this?

This is a simple proxy that uses [cloudscraper](https://github.com/venomous/cloudscraper) to bypass Cloudflare's anti-bot page.

### How to use?

* Create a `config.yml` file like this:
```
mkdir .dev
cat << EOF > .dev/config.yml
---
log:
  dev: False
EOF
```
* Run docker compose:
```
docker compose up -d
```
* Test it:
```
curl -X POST localhost:8080/agent/persistent
```
* To refresh and build the container again:
```
docker compose build --no-cache
```

### How to develop?

* Install [pyenv](https://github.com/pyenv/pyenv#installation)
* Install the desired Python >= 3.12: `pyenv install 3.12` 
* Create a virtualenv: `pyenv virtualenv 3.12 cloudscraper-proxy`
* Activate the virtualenv: `pyenv activate cloudscraper-proxy`
* Install the dependencies: `MEINHELD_NOGREEN=1 pip install --only-binary greenlet -r requirements.txt`
* Run the proxy with built-in Flask server: `PYTHONPATH="${PYTHONPATH}:." python main.py`
* Run the proxy with Gunicorn: `PYTHONPATH="${PYTHONPATH}:."  gunicorn -b 0.0.0.0:8080 -c utils/gunicorn_config.py --logger-class utils.gunicorn_structlog.GunicornLogger wsgi:app`
* Run the tests: `PYTHONPATH="${PYTHONPATH}:." coverage run -m unittest discover tests/`
* Deactivate the virtualenv: `pyenv deactivate`

If you're using VSCode, `launch.json` is included, so you can run development with F5.

**Development notes**

* Don't forget to update `__version__.py` when you make changes according to [semver](https://semver.org/).
* Update and run unit tests before pushing.
* For commit messages forllow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
