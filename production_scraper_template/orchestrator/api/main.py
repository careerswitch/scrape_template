from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import os
import json
from supabase import create_client

app = FastAPI()

REDIS_URL = os.getenv('REDIS_URL')
r = redis.from_url(REDIS_URL)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class JobCreate(BaseModel):
    start_url: str
    max_depth: int = 3
    selectors: dict = {}

 @app.post('/jobs')
def create_job(payload: JobCreate):
    # persist job in Supabase jobs table
    job = supabase.table('jobs').insert({
        'start_url': payload.start_url,
        'status': 'queued',
        'meta': {'max_depth': payload.max_depth, 'selectors': payload.selectors}
    }).execute()
    if job.error:
        raise HTTPException(status_code=500, detail=str(job.error))
    job_id = job.data[0]['id']

    # push message to Redis queue
    message = json.dumps({
        'job_id': job_id,
        'start_url': payload.start_url,
        'max_depth': payload.max_depth,
        'selectors': payload.selectors
    })
    r.lpush('queue:jobs', message)
    return {'job_id': job_id}
