from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel
import os

load_dotenv()

ENV_MODE = os.getenv("ENV_MODE", "development")

if ENV_MODE == "production":
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://todo-list-iohl.onrender.com"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class PostCreate(BaseModel):
    title: str
    completed: bool = False

@app.get("/lists")
def get_lists():
    response = supabase.table("lists").select("*").order("created_at", desc=True).execute()
    return response.data

@app.post("/lists")
def create_list(post: PostCreate):
    response = supabase.table("lists").insert({
        "title": post.title,
        "completed": post.completed
    }).execute()
    return response.data[0]

@app.delete("/lists/{list_id}")
def delete_list(list_id: int):
    response = supabase.table("lists").delete().eq("id", list_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}

@app.put("/lists/{list_id}")
def update_list(list_id: int, post: PostCreate):
    response = supabase.table("lists").update({
        "title": post.title,
        "completed": post.completed
    }).eq("id", list_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="List not found")
    return response.data[0]
