from fastapi import FastAPI, Body, Path, Query, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

app = FastAPI(
    title="Aprendiendo FastAPI",
    description="Aprendiendo a crear una API con FastAPI",
    version="0.0.1",
)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Invalid email")

class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(default="Mi pelicula", min_length= 5, max_length=15)
    overview: str
    year: int
    rating: float
    category: str

movies = [
    {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Acción"
	},
    {
		"id": 2,
		"title": "Avatar 2, el mundo del agua",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2022",
		"rating": 8.2,
		"category": "Aventura"
	}
]

## Login
@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content=token)

## movies

@app.get("/", tags=['home'])
def root():
    return HTMLResponse(content="<h1>API de ejemplo</h1>", status_code=200)

@app.get('/movies', tags=['movies'], response_model=List, status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies():
    html_content = ""
    for movie in movies:
        html_content += f"""
        <h2>{movie['title']}</h2>
        <p>{movie['overview']}</p>
        <p>{movie['year']}</p>
        <p>{movie['rating']}</p>
        <p>{movie['category']}</p>
        """
    #return HTMLResponse(content=html_content, status_code=200)
    return JSONResponse(content=movies, status_code=200)

# params
@app.get('/movies/{movie_id}', tags=['movies'])
def get_movie(movie_id: int = Path(ge=1, le=2000)):
    movie = [movie for movie in movies if movie['id'] == movie_id]
    if len(movie) == 0:
        return HTMLResponse(content="<h1>Película no encontrada</h1>", status_code=404)
    movie = movie[0]
    html_content = f"""
    <h2>{movie['title']}</h2>
    <p>{movie['overview']}</p>
    <p>{movie['year']}</p>
    <p>{movie['rating']}</p>
    <p>{movie['category']}</p>
    """
    return HTMLResponse(content=html_content, status_code=200)

# query params
@app.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    html_content = ""
    for movie in movies:
        if movie['category'] == category:
            html_content += f"""
            <h2>{movie['title']}</h2>
            <p>{movie['overview']}</p>
            <p>{movie['year']}</p>
            <p>{movie['rating']}</p>
            <p>{movie['category']}</p>
            """
    return HTMLResponse(content=html_content, status_code=200)

@app.post('/movies', tags=['movies'], response_model=dict)
def create_movie(movie: Movie):
    movies.append(movie)
    return JSONResponse(content={"message": "Pelicula creada"}, status_code=201)

@app.put('/movies/{movie_id}', tags=['movies'])
def update_movie(movie_id: int, movie: Movie):
    for item in movies:
        if item["id"] == movie_id:
            item["title"] = movie.title
            item["overview"] = movie.overview
            item["year"] = movie.year
            item["rating"] = movie.rating
            item["category"] = movie.category
            return item

@app.delete('/movies/{movie_id}', tags=['movies'])
def delete_movie(movie_id: int):
    for item in movies:
        if item["id"] == movie_id:
            movies.remove(item)
            return {"message": "Película eliminada"}