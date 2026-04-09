# Arquivo main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col

from math import ceil

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

# app.mount("/Static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
 
TAMANHO_PAGINA = 10
def buscar_alunos(busca: str, pagina: int=1):
    with Session(engine) as session:
            query = select(Aluno)
            if busca:
                query = query.where(col(Aluno.nome).contains(busca))
            
            query = query.order_by(Aluno.nome)
            
            # 1. Count the total matching records to calculate pages
            total_alunos = len(session.exec(query).all())
            total_paginas = ceil(total_alunos / TAMANHO_PAGINA)
            
            # Prevent "Page 0" if the search has no results
            if total_paginas == 0: 
                total_paginas = 1
                
            # 2. SQL Offset and Limit
            skip = (pagina - 1) * TAMANHO_PAGINA
            alunos_paginados = session.exec(query.offset(skip).limit(TAMANHO_PAGINA)).all()
            
            return alunos_paginados, total_paginas
        
@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None='', pagina: int = 1):
    if busca is None: 
        busca = ''
        
    alunos, total_paginas = buscar_alunos(busca, pagina)
    
    # Pass the new variables to Jinja2
    return templates.TemplateResponse(request, "lista.html", {
        "alunos": alunos, 
        "busca": busca,
        "pagina": pagina,
        "total_paginas": total_paginas
    })

@app.get("/editarAlunos")
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")
    
    
@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        # FIX: Return an HTML error message instead of crashing with 404
        if not aluno:
            return HTMLResponse(
                content=f"<div style='color: #ff4444; margin-top: 5px;'>"
                        f"❌ Erro: Aluno com ID {id} não encontrado!</div>"
            )
            
        session.delete(aluno)
        session.commit()
        return HTMLResponse(
            content=f"<div style='color: #00ff00; margin-top: 5px;'>"
                    f"✅ O(a) aluno(a) {aluno.nome} foi deletado(a)!</div>"
        )

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>")
    
@app.delete("/apagar", response_class=HTMLResponse)
def apagar():
    return ""