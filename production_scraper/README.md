# production_scraper

Production-ready Scrapy worker + Redis queue + Supabase storage scaffold.

**Quick start (dev)**

1. Create a virtualenv and install deps:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Set these env vars locally for dev (use a .env file or your shell):

* `SUPABASE_URL` - your supabase url
* `SUPABASE_KEY` - your supabase service role key (keep secure)
* `REDIS_URL` - e.g. redis://localhost:6379/0
* `JOB_ID` (for manual testing)

3. Run a local spider (for dev only):

```bash
scrapy crawl robust
```

**Production**: build the Docker image and deploy to Kubernetes or run in your cloud container service. Use Kubernetes manifests in `k8s/` as a starting point.

```
```
