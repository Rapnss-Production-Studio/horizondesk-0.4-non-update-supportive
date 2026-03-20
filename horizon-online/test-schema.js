fetch("https://horizon-online.api-rapnss.workers.dev/api/debug/schema")
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
