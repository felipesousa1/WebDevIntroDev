from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select, SQLModel, create_engine
from models import Aluno, Tarefa
from contextlib import asynccontextmanager

arquivo_sqlite = "exercicio_7.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("Banco de dados e tabelas criados com sucesso!")
    yield
    print("Desligando o servidor...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "API está rodando!"}

@app.post("/alunos")
def criar_aluno(aluno: Aluno):
    with Session(engine) as session:
        session.add(aluno)
        session.commit()
        session.refresh(aluno)
        return aluno


@app.post("/tarefas")
def criar_tarefa(tarefa: Tarefa):
    with Session(engine) as session:
        session.add(tarefa)
        session.commit()
        session.refresh(tarefa)
        return tarefa


@app.get("/alunos")
def listar_alunos():
    with Session(engine) as session:
        return session.exec(select(Aluno)).all()

@app.get("/tarefas")
def listar_tarefas():
    with Session(engine) as session:
        return session.exec(select(Tarefa)).all()

@app.get("/alunos/{aluno_nusp}/tarefas")
def listar_tarefas_do_aluno(aluno_nusp: int):
    with Session(engine) as session:
        aluno = session.get(Aluno, aluno_nusp)
        
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        return aluno.tarefas