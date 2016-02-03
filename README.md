# Focus Group Logs Flask frontend


## To build

`docker build -t focusgrouplogs .`


## To run

```bash
docker run -d --name=focusgrouplogs \
-e FOCUSGROUPLOGS_LOGDIR=/data \
-v /data/focusgrouplogs:/data \
-p 8080:8080 \
focusgrouplogs
```

Additionally, for the datastore backend, you will need the following env vars set:

`GCLOUD_DATASET_ID`: string, your google project ID
`GOOGLE_APPLICATION_CREDENTIALS` filepath to your API credentials json file
`FOCUGROUPLOGS_BACKEND`: set this to "datastore", default is "files"
`TRANSITION_TO_DATASTORE`: set to "1" to enable a /migrate route to transition from files to datastore


## Log format

From the `FOCUSGROUPLOGS_LOGDIR` root, there are folders per focus group. The
`legacy` folder has some special handling due to having inconsistent names and
having log messages spanning multiple days.

In each folder down from the logdir root it is expected that there is a list of
`.txt` files following the convention: `YYYY-MM-DD.focusgroupname.txt`.

Each entry in the log files are in the following format:

`[YYYY-MM-DD HH:MM:SS] <irc_username> message ...`


## The future

I want to get this off of files/filesystems as soon as possible. The data is
perfect for storing as key/value, and [google gives us one to use](https://cloud.google.com/datastore/docs/concepts/overview).
Need to update the feeder container to use this first, and make those changes
in lockstep.

The cache times on the file reads are probably too short, but for now I'd
rather err on the side of freshness.

Need to come up with a better view for the main page. Would like to have each
month grouped together with a [+]/[-] button to expand/collaspe the month.
Currently it's not too bad, but eventually it's going to be a really long page.

Will change the cache type to redis someday, but not until after the filesystem
change, since that locks the frontend deployment to a single node anyway.


## Get involved!

See something off? Something that can be improved? Fork and send a pull request!
