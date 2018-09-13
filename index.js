const BigQuery = require('@google-cloud/bigquery');
const bigquery = new BigQuery({
  projectId: process.env.GCLOUD_PROJECT
})

exports.event = (req, res) => {
  if (req.method === `OPTIONS`) {
    res.set('Access-Control-Allow-Origin', '*').set('Access-Control-Allow-Methods', 'OPTIONS, POST').status(200);
    return;
  } else if (req.method === `POST`) {
    let body = JSON.parse(req.body)
    if (body.type === undefined) {
      res.status(400).send("Invalid event type " + body.type)
      return;
    }
    rows = [{type: body.type, created: Date.now() / 1000, properties: JSON.stringify(body.properties)}];

    bigquery.dataset('standard').table('events').insert(rows)
      .then(() => {
        res.set('Access-Control-Allow-Origin', '*').set('Access-Control-Allow-Methods', 'OPTIONS, POST').status(200);
        res.status(200).send();
        return;
      })
      .catch(err => {
        console.error(err);
        res.status(400).send('BigQuery insertion failed. Check your standard.events table schema.');
        return;
      });
  } else {
    res.status(400).send('Bad method')
  }
};
