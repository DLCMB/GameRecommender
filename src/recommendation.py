import pandas as pd
from pathlib import Path


class GameRecommender:
    """Motor de recomendación basado en contenido (similitud de géneros)."""

    def __init__(self, data_path: Path):
        # 1. Cargar datos en memoria al instanciar la clase
        self.df = pd.read_csv(data_path)

        # 2. Preprocesamiento: Convertir el texto "Action, RPG" en un Set de Python {'Action', 'RPG'}
        # Los Sets (conjuntos) tienen complejidad O(1) para búsquedas, ideal para algoritmos.
        self.df['genre_set'] = self.df['genres'].fillna("").apply(
            lambda x: set(x.split(", ")) if x != "Unknown" and x else set()
        )

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calcula el coeficiente de Jaccard entre dos conjuntos."""
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def recommend(self, game_name: str, top_k: int = 5) -> pd.DataFrame:
        """Devuelve los top_k juegos más similares al título dado."""

        # 1. Buscar el juego ignorando mayúsculas/minúsculas
        target_game = self.df[self.df['name'].str.lower() == game_name.lower()]

        if target_game.empty:
            print(f"Error: No se ha encontrado el juego '{game_name}' en la base de datos.")
            return pd.DataFrame()

        # Extraemos los géneros del juego objetivo
        target_genres = target_game.iloc[0]['genre_set']
        target_id = target_game.iloc[0]['id']

        if not target_genres:
            print(f"El juego '{game_name}' no tiene géneros registrados para comparar.")
            return pd.DataFrame()

        # 2. Aplicar el algoritmo a todos los demás juegos
        # Hacemos una copia para no modificar el dataset original
        recommendations = self.df[self.df['id'] != target_id].copy()

        recommendations['similarity'] = recommendations['genre_set'].apply(
            lambda x: self._jaccard_similarity(target_genres, x)
        )

        # 3. Ordenar por similitud (descendente) y luego por valoración (descendente)
        # Así, si hay empate de géneros, te recomienda el mejor juego.
        recommendations = recommendations.sort_values(
            by=['similarity', 'rating'], ascending=[False, False]
        )

        # Devolvemos solo las columnas limpias y los primeros 'top_k' resultados
        return recommendations[['name', 'genres', 'rating', 'similarity']].head(top_k)


if __name__ == "__main__":
    # Ruta absoluta al archivo de datos que descargamos en la Fase 1
    base_dir = Path(__file__).resolve().parent.parent
    data_file = base_dir / "data" / "raw" / "igdb_games.csv"

    if not data_file.exists():
        print("No se encuentra el archivo de datos. ¡Ejecuta primero data_extraction.py!")
    else:
        # Instanciamos el recomendador
        recommender = GameRecommender(data_path=data_file)

        # Lista de juegos de prueba. ¡Cambia estos nombres por juegos que sepas que están en tu CSV!
        juegos_prueba = ["The Witcher 3: Wild Hunt", "Elden Ring", "Portal 2", "Terraria: Calamity Mod"]

        for juego in juegos_prueba:
            print(f"\n--- Recomendaciones para: {juego} ---")
            resultados = recommender.recommend(game_name=juego, top_k=3)

            if not resultados.empty:
                print(resultados.to_string(index=False))