# Chord

[Simple analytics](https://en.wikipedia.org/wiki/Circular_segment) for collecting event data (like pageviews) on top of Google Cloud Functions and BigQuery.

## Setup

```sh
gcloud beta functions deploy event --trigger-http
```

Create a BigQuery dataset named `analytics` and a table named `event` with the schema:

| Column    | Type      | Constraint |
| --------- | --------- | ---------- |
| type      | STRING    | REQUIRED   |
| timestamp | TIMESTAMP | REQUIRED   |
| data      | STRING    | NULLABLE   |

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

Build the minimized JS with: `npm run build`
