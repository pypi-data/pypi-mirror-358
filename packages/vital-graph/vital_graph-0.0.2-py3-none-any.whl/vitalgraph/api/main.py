import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import FastAPI, Request, Form, Depends
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
from pathlib import Path
import uvicorn


package_dir = Path(__file__).resolve().parent.parent  # points at vitalgraph/

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "CHANGE_THIS"))
templates = Jinja2Templates(directory=package_dir / "templates")

app.mount(
    "/static",
    StaticFiles(directory="vitalgraph/web_assets/"),
    name="static"
)

def valid_user(username: str, password: str) -> bool:
    # only one dummy user
    return username == "admin" and password == "admin"

def get_current_user(request: Request) -> Optional[str]:
    return request.session.get("user")

def require_user(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return user

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # redirect based on session
    if not get_current_user(request):
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url="/spaces", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not valid_user(username, password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })
    # store in session
    request.session["user"] = username
    return RedirectResponse(url="/spaces", status_code=302)

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/spaces", response_class=HTMLResponse)
async def list_spaces(request: Request, user=Depends(require_user)):
    # dummy space list
    spaces = [
        {"id": 1, "name": "RDF Graph",   "type": "rdf_graph"},
        {"id": 2, "name": "Vital Graph", "type": "vital_graph"},
    ]
    return templates.TemplateResponse("spaces.html", {
        "request": request,
        "user": user,
        "spaces": spaces
    })

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("vitalgraph.api.main:app", host="0.0.0.0", port=8001, reload=True)

