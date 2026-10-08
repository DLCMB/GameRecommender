import streamlit as st
from pathlib import Path
from recommendation import GameRecommender

# 1. Configuración básica de la página web
st.set_page_config(page_title="Recomendador de Juegos", page_icon="🎮", layout="centered")
st.title("🎮 Motor de Recomendación de Videojuegos")
st.write("Encuentra tu próximo juego favorito basado en la similitud matemática de géneros.")


# 2. Cargar datos en caché (Buenas prácticas)
# El decorador @st.cache_resource evita que la base de datos se vuelva a cargar en memoria cada vez que haces clic
@st.cache_resource
def load_recommender():
    base_dir = Path(__file__).resolve().parent.parent
    data_file = base_dir / "data" / "raw" / "igdb_games.csv"
    return GameRecommender(data_path=data_file)


try:
    recommender = load_recommender()

    # Extraemos todos los nombres de juegos únicos y los ordenamos alfabéticamente para el menú
    lista_juegos = recommender.df['name'].sort_values().unique()

    # 3. Elementos de la interfaz de usuario
    # Creamos dos columnas para organizar los controles
    col1, col2 = st.columns([3, 1])

    with col1:
        juego_seleccionado = st.selectbox("Elige un juego como referencia:", lista_juegos)
    with col2:
        top_k = st.number_input("Resultados:", min_value=1, max_value=20, value=5)

    # 4. Botón de ejecución
    if st.button("Buscar Recomendaciones", type="primary"):
        with st.spinner("Calculando similitudes..."):
            resultados = recommender.recommend(juego_seleccionado, top_k)

            if not resultados.empty:
                st.success("¡Análisis completado!")

                # Renderizamos la tabla de Pandas de forma visual y atractiva
                st.dataframe(
                    resultados[['name', 'genres', 'rating', 'similarity']],
                    column_config={
                        "name": "Título",
                        "genres": "Géneros",
                        "rating": st.column_config.NumberColumn("Valoración", format="%.1f / 100"),
                        "similarity": st.column_config.ProgressColumn(
                            "Índice de Similitud",
                            min_value=0.0,
                            max_value=1.0
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("No se encontraron recomendaciones suficientes.")

except FileNotFoundError:
    st.error("Error: No se encuentra el archivo igdb_games.csv. Ejecuta primero la Fase 1.")