# Focus Group Logs Flask frontend


## To build

`docker build -t focusgrouplogs .`


## To run

```bash
docker run -d --name=focusgrouplogs \
-e FOCUSGROUPLOGS_LOGDIR=/data \
-e FOCUS_GROUPS="capitals tactical-destroyers" \
-v /data/focusgrouplogs:/data \
-p 8080:8080 \
focusgrouplogs
```

Additionally, for the datastore backend, you will need the following env vars set:

* `GCLOUD_DATASET_ID`: string, your google project ID
* `GOOGLE_APPLICATION_CREDENTIALS` filepath to your API credentials json file
* `FOCUGROUPLOGS_BACKEND`: set this to "datastore", default is "files"
* `TRANSITION_TO_DATASTORE`: set to "1" to enable a /migrate route to transition from files to datastore


## Caching

Setting the `FOCUSGROUPLOGS_REDIS` env var to "1" will enable redis caching.
By default it will use "redis:6379/0" for a host and database. Use the
`FOCUSGROUPLOGS_REDIS_URL` env var to change that to suit your needs.

If you want to use redis caching in dev, run the following before your start
your frontend container

```bash
docker run -d --name=focusgrouplogs-redis \
-p 6379:6379 \
redis:latest
```

Then add `--link=focusgrouplogs-redis:redis` to your run args for the frontend
container, and use `-e FOCUSGROUPLOGS_REDIS=1` to enable using the redis cache.


## Log format (files backend)

From the `FOCUSGROUPLOGS_LOGDIR` root, there are folders per focus group. The
`legacy` folder has some special handling due to having inconsistent names and
having log messages spanning multiple days.

In each folder down from the logdir root it is expected that there is a list of
`.txt` files following the convention: `YYYY-MM-DD.focusgroupname.txt`.

Each entry in the log files are in the following format:

`[YYYY-MM-DD HH:MM:SS] <irc_username> message ...`


## The future

Need to come up with a better view for the main page. Would like to have each
month grouped together with a [+]/[-] button to expand/collaspe the month.
Currently it's not too bad, but eventually it's going to be a really long page.

I'll probably remove the datastore migration and files backend after a while.

Need to come up with a better way to show all logs from a group. Probably do some
fancy infinite loading page, make a JSON response for the group/date routes.


## Get involved!

See something off? Something that can be improved? Fork and send a pull request!
