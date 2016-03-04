# Focus Group Logs Flask frontend


## To build

`docker build -t focusgrouplogs .`


## To run

```bash
docker run -d --name=focusgrouplogs \
-e GCLOUD_DATASET_ID="your-google-project-ID" \
-e GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json" \
-v /data/focusgrouplogs:/data \
-p 8080:8080 \
focusgrouplogs
```


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

Also be sure to add `--link=focusgrouplogs-redis:redis` to your run args for
the frontend container.


## Debugging

To debug this container for local dev work, add the command
`/venv/bin/python /app/focusgrouplogs/web.py` to your docker run command. This
will run flask in debug, you can find the PIN via `docker logs focusgrouplogs`.


## The future

Need to come up with a better way to show all logs from a group. Probably do some
fancy infinite loading page, make a JSON response for the group/date routes.


## Get involved!

See something off? Something that can be improved? Fork and send a pull request!
