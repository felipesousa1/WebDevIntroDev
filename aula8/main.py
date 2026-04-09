from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Ex 1
likes_count = 0

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"likes": likes_count}
    )

# Ex 1 e 2
@app.post("/curtir")
def processar_curtida(zerar: bool = False):
    global likes_count
    if zerar:
        likes_count = 0
    else:
        likes_count += 1
        
    return HTMLResponse(content=str(likes_count))

# Ex 3
@app.get("/abas/{nome_aba}")
def carregar_aba(request: Request, nome_aba: str):

    return templates.TemplateResponse(
        request=request, 
        name=f"{nome_aba}.html", 
        context={"likes": likes_count}
    )