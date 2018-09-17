# Chord

[Simple analytics](https://en.wikipedia.org/wiki/Circular_segment) for collecting event data (like pageviews) on top of Google Cloud Functions and BigQuery.

TODOs: Support BigQuery and Postgres, BULK insert

Right now, it only supports `standard.events` table.

## Setup

Setup should take <10 minutes.

1. Signup for GCP and enable billing (needed for BigQuery)

2. Install `gcloud` SDK locally

3. Clone this repo and from within the repo, run

```sh
gcloud beta functions deploy event --trigger-http
```

4. Create BigQuery table `standard.events` from the BigQuery UI. Recommend that you partition by `created` column.

| Column     | Type      | Constraint |
| ---------- | --------- | ---------- |
| type       | STRING    | REQUIRED   |
| created    | TIMESTAMP | REQUIRED   |
| properties | STRING    | NULLABLE   |

5. Add js scripts

Build the minimized JS `npm run build` and add it to your frontend.

```html
<script src="chord.min.js"></script>

...

<script>
chord.endpoint = "<GCP FUNCTIONS ENDPOINT>";
chord.identify(<user_id>);
chord.event('page');
</script>
```

6. Bonus: Create convenience views

Create a `standard.views` views for easier access to pageviews.

Views are relatively intelligent, so they respect the date-partitioning of the original `standard.events` table, so it's just as performant.

### `standard.views`

```sql
select
	created
	, json_extract_scalar(properties, '$.url') as url
	, json_extract_scalar(properties, '$.referrer') as referrer
	, json_extract_scalar(properties, '$.ip_address') as ip_address
	, json_extract_scalar(properties, '$.user_agent') as user_agent
	, json_extract_scalar(properties, '$.session_id') as session_id
	, json_extract_scalar(properties, '$.viewer_id') as viewer_id
	, json_extract_scalar(properties, '$.user_id') as user_id
	, properties
from `<gcp-project-id>.standard.events`
```
