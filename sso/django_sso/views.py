from fastapi import FastAPI
# import cache
import json
from django.http import HttpResponse

app = FastAPI()

@app.get("/")
async def root(req):
    return HttpResponse({"message": "Hello World"})

# POST /login/callback
@app.post("/login")
async def login(req):
    return HttpResponse("login")

@app.post("/token")
async def token(req, response):
    return HttpResponse("token")

@app.post("/renew")
async def renew(req):
    return HttpResponse("renew")

@app.post("/revoke")
async def revoke(req):
    return HttpResponse("revoke")