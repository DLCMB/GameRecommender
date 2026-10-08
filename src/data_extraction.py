import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Cargar las variables del .env
load_dotenv()


def get_twitch_token(client_id: str, client_secret: str) -> str:
    """Se autentica en Twitch y devuelve un token de acceso temporal."""
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_igdb_games(client_id: str, token: str) -> pd.DataFrame:
    """Extrae datos de juegos de IGDB usando el token de Twitch."""
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}"
    }

    # Consulta simplificada: dame 100 juegos que tengan alguna valoración
    query = (
        "fields id, name, total_rating, genres.name; "
        "where total_rating > 0; "
        "sort total_rating desc; "
        "limit 100;"
    )

    try:
        response = requests.post(url, headers=headers, data=query)

        # Si hay un error 400 (mala consulta), lo capturamos e imprimimos el motivo real
        if response.status_code != 200:
            print(f"Error de la API. Código {response.status_code}: {response.text}")
            return pd.DataFrame()

        data = response.json()
        print(f"-> ¡Éxito! La API ha devuelto {len(data)} juegos crudos.")

        all_games = []
        for game in data:
            game_data = {
                "id": game.get("id"),
                "name": game.get("name"),
                "rating": game.get("total_rating"),
                "genres": ", ".join([g["name"] for g in game.get("genres", [])]) if "genres" in game else "Unknown"
            }
            all_games.append(game_data)

        return pd.DataFrame(all_games)

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con IGDB: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
    CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Faltan las credenciales de IGDB en el archivo .env")

    print("1. Obteniendo token de autenticación de Twitch...")
    token = get_twitch_token(CLIENT_ID, CLIENT_SECRET)

    print("2. Descargando datos de videojuegos...")
    df_games = fetch_igdb_games(CLIENT_ID, token)

    if not df_games.empty:
        # Guardado profesional con rutas absolutas
        base_dir = Path(__file__).resolve().parent.parent
        output_dir = base_dir / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "igdb_games.csv"
        df_games.to_csv(output_path, index=False)

        print(f"\n¡Éxito! Se han guardado {len(df_games)} juegos en: {output_path}")
        print("\nMuestra de los datos:")
        print(df_games.head())
    else:
        print("No se encontraron datos.")