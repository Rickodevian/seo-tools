# Seo Tools

Seo Tools is a tool to get backlink, citation flow, and trusflow of a website. This program is write with python and scrapy framework for scraping. there's 2 spiders in this project, `siteReport` and `backlinkChecker`. Use `siteReport` spider to get citation flow and trustflow value from specified website. Use `backlinkChecker` spider to retrieve all urbanindo backlinks from specified website.

## Requirements
- scrapy
- scrapyd
- scrapyd-client
- fake-useragent
- mysql-python


## Installation
- install scrapy. you can install scrapy with pip by execute this command
```
pip install scrapy
```
- install scrapyd to deploy the project and run them. You can install scrapyd using pip by execute this command
```
pip install scrapyd
```
- alternatively you can deploy the project using scrapyd-client, scrapyd client will automatically create egg of the project and deploy it. clone the project at [scrapyd client github page](https://github.com/scrapy/scrapyd-client) and then install it.
```
git clone git@github.com:scrapy/scrapyd-client.git
python setup.py
```
- install fake user agent
```
pip install fake-useragent
```
- install mysql python
```
sudo apt-get install python-dev libmysqlclient-dev
pip install MySQL-python
```

## Deploying Project
Deploying project involves eggifying it and uploading the egg to scrapyd via `addversion.json` endpoint. you can do it using scrapyd deploy tool provided by scrapyd client.
- create egg file of the project
```
scrapyd-deploy --build-egg=FILE
```
- deploy egg file to `addversion.json` endpoint
```
curl http://localhost:6800/addversion.json -F project=myproject -F version=r23 -F egg=@myproject.egg
```

## Run Project
You can run the project by accessing the `schedule.json` API from scrapyd. you set which project you want to run, set spider and url to scrape.
```
curl http://localhost:6800/schedule.json -d project=seo -d spider=siteReport -d url="http://www.google.com"
```
it will return
```
{"status": "ok", "jobid": "6487ec79947edab326d6db28a2d86511e8247444"}
```
your job is registered and will be executed by scrapyd. check [Scrapyd Documentation Page](https://scrapyd.readthedocs.io/en/latest/api.html) for more option. 