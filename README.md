# Chord

[Simple analytics](https://en.wikipedia.org/wiki/Circular_segment) for collecting event data (like pageviews) on top of Google Cloud Functions and BigQuery.

## Setup

### Setup Cloud Functions

You'll need to enable billing, etc from within the cloud console as well as install `gcloud` locally.

```sh
gcloud beta functions deploy event --trigger-http
```

### Setup BigQuery

Create a BigQuery dataset named `analytics` and a table named `event` with the schema:

| Column    | Type      | Constraint |
| --------- | --------- | ---------- |
| type      | STRING    | REQUIRED   |
| timestamp | TIMESTAMP | REQUIRED   |
| data      | STRING    | NULLABLE   |

### Add js scripts

```html
<script src="chord.min.js"></script>

...

<script>
chord.endpoint = "<GCP FUNCTIONS ENDPOINT>";
chord.identify(<user_id>);
chord.event('page');
</script>
```

## Optional

Build the minimized JS yourself with: `npm run build`
