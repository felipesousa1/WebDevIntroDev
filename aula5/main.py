from fastapi import FastAPI, Request, Response, Depends, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

# Tells FastAPI where to find the HTML files
templates = Jinja2Templates(directory="templates")

# Our fake database (a list of dictionaries)
users_db = []

# --- MODELS ---
# These act as strict rules. If JS sends data that doesn't match this, FastAPI blocks it.
class User(BaseModel):
    nome: str
    senha: str
    bio: str

class LoginData(BaseModel):
    nome: str
    senha: str
    
# --- ROUTES ---

# 1. Shows the Register Page
@app.get("/")
def show_register(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

# 2. Receives the JS Fetch from Register Page
@app.post("/users")
def create_user(user: User):
    # .model_dump() converts the Pydantic object into a standard Python dictionary
    users_db.append(user.model_dump())
    return {"message": "Usuário criado"}

# 3. Shows the Login Page
@app.get("/login")
def show_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# 4. Receives the JS Fetch from Login Page and Sets Cookie
@app.post("/login")
def process_login(data: LoginData, response: Response):
    # Loop through our database to find a matching name and password
    for user in users_db:
        if user["nome"] == data.nome and user["senha"] == data.senha:
            # Match found! Give the browser a "VIP ticket" (Cookie)
            response.set_cookie(key="session_user", value=data.nome)
            return {"message": "Login ok"}
    
    # If the loop finishes and finds nothing, block them.
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

# --- AUTHENTICATION LOGIC ---

# The Security Guard Function
def get_active_user(session_user: str | None = Cookie(None)):
    # Did the browser bring the VIP ticket?
    if not session_user:
        raise HTTPException(status_code=401, detail="Não está logado")
    
    # Does the name on the ticket exist in our database?
    for user in users_db:
        if user["nome"] == session_user:
            return user # Hand the user data to the route
            
    raise HTTPException(status_code=401, detail="Sessão inválida")

# 5. Shows the Profile Page (Protected)
@app.get("/home")
def show_home(request: Request, current_user: dict = Depends(get_active_user)):
    # Depends() stops everything. If get_active_user fails, this code never runs.
    # If it passes, current_user gets the dictionary, and we pass it to profile.html
    return templates.TemplateResponse(
        request=request, 
        name="profile.html", 
        context={"user": current_user}
    )