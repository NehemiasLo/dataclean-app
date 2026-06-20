import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

# Configuraci�n de la p�gina web
st.set_page_config(
    page_title="DataClean - Limpieza Inteligente de Datos",
    page_icon="?",
    layout="wide"
)

# Estilos de encabezado
st.title("? DataClean Automatizado")
st.markdown("### Transforma datasets sucios en datos listos para producci�n, sin escribir una sola l�nea de c�digo.")
st.write("---")

# 1. Carga de Archivos
uploaded_file = st.file_uploader(
    "Selecciona o arrastra tu archivo aqu� (Formatos admitidos: .csv, .xlsx)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        # Carga del DataFrame
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("�Archivo cargado exitosamente!")

        # 2. Diagn�stico Inicial del Dataset
        st.subheader("? Diagn�stico Inicial del Dataset")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Vista previa de los datos originales (Primeras 5 filas):**")
            st.dataframe(df.head(5), use_container_width=True)

        with col2:
            st.markdown("**Resumen de anomal�as encontradas:**")
            total_filas, total_cols = df.shape
            filas_duplicadas = int(df.duplicated().sum())
            total_nulos = int(df.isnull().sum().sum())

            st.metric(label="Dimensiones (Filas x Columnas)", value=f"{total_filas} x {total_cols}")
            st.metric(label="Filas Duplicadas", value=filas_duplicadas,
                      delta=-filas_duplicadas if filas_duplicadas > 0 else 0, delta_color="inverse")
            st.metric(label="Celdas con Valores Nulos", value=total_nulos, delta=-total_nulos if total_nulos > 0 else 0,
                      delta_color="inverse")

        st.write("---")

        # 3. Procesamiento y pipeline de limpieza al presionar el bot�n
        st.subheader("? Procesamiento Autom�tico")
        st.info(
            "El sistema aplicar� transformaciones autom�ticas de tipos, limpieza de monedas, correcci�n de outliers, imputaci�n de nulos y estandarizaci�n de texto.")

        if st.button("? Ejecutar Pipeline de Limpieza Completo", type="primary"):
            with st.spinner("Procesando y saneando el dataset..."):

                df_cleaned = df.copy()
                logs = []

                # --- A. Inferencia de Tipos ---
                for col in df_cleaned.columns:
                    if 'date' in col.lower() or 'time' in col.lower():
                        temp_series = pd.to_datetime(df_cleaned[col], errors='coerce')
                        if temp_series.notna().sum() / len(df_cleaned) > 0.8 and temp_series.notna().sum() > 0:
                            df_cleaned[col] = temp_series
                            logs.append(f"? Columna **'{col}'** convertida a tipo Fecha/Hora (datetime).")
                            continue

                    temp_series = pd.to_numeric(df_cleaned[col], errors='coerce')
                    if not pd.api.types.is_numeric_dtype(df_cleaned[col]) and (
                            temp_series.notna().sum() / len(df_cleaned) > 0.8):
                        df_cleaned[col] = temp_series
                        logs.append(f"? Columna **'{col}'** convertida a tipo Num�rico.")
                        continue

                    if not pd.api.types.is_datetime64_any_dtype(df_cleaned[col]) and not pd.api.types.is_numeric_dtype(
                            df_cleaned[col]):
                        df_cleaned[col] = df_cleaned[col].astype(object)

                # --- B. Formatos de Moneda ---
                for col in df_cleaned.select_dtypes(include='object').columns:
                    combined_string = ' '.join(df_cleaned[col].astype(str).dropna().tolist())
                    currency_pattern = r'[?$��]'
                    if pd.Series(combined_string).str.contains(currency_pattern, regex=True).any() or \
                            (df_cleaned[col].astype(str).str.contains(
                                r'^\s*[+-]?(?:\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*$',
                                regex=True).all()):

                        cleaned_series = df_cleaned[col].astype(str).str.replace(currency_pattern, '', regex=True)
                        num_commas = cleaned_series.str.count(',').sum()
                        num_dots = cleaned_series.str.count('\.').sum()

                        if num_commas > num_dots and num_commas > 0:
                            cleaned_series = cleaned_series.str.replace('.', '', regex=False).str.replace(',', '.',
                                                                                                          regex=False)
                        else:
                            cleaned_series = cleaned_series.str.replace(',', '', regex=False)

                        df_cleaned[col] = pd.to_numeric(cleaned_series, errors='coerce')
                        logs.append(f"? Formato de moneda corregido y unificado en columna **'{col}'**.")

                # --- C. Tratamiento de Outliers (Mediana IQR) ---
                for col in df_cleaned.select_dtypes(include=np.number).columns:
                    if df_cleaned[col].dropna().empty:
                        continue
                    Q1 = df_cleaned[col].quantile(0.25)
                    Q3 = df_cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outliers_mask = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
                    outliers_count = outliers_mask.sum()
                    if outliers_count > 0:
                        median_val = df_cleaned[col].median()
                        df_cleaned.loc[outliers_mask, col] = median_val
                        logs.append(
                            f"? Columna **'{col}'**: {outliers_count} valores at�picos reemplazados por la mediana ({median_val}).")

                # --- D. Imputaci�n de Valores Faltantes ---
                for col in df_cleaned.columns:
                    if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                        if df_cleaned[col].isnull().any():
                            median_val = df_cleaned[col].median()
                            df_cleaned[col] = df_cleaned[col].fillna(median_val)
                            logs.append(
                                f"? Columna **'{col}'**: Valores nulos num�ricos imputados con la mediana ({median_val}).")
                    elif pd.api.types.is_object_dtype(df_cleaned[col]):
                        df_cleaned[col] = df_cleaned[col].replace(
                            {'': np.nan, 'nan': np.nan, 'NaN': np.nan, 'None': np.nan, 'N/A': np.nan})
                        df_cleaned[col] = df_cleaned[col].replace(r'^\s*$', np.nan, regex=True)

                        if df_cleaned[col].isnull().any():
                            mode_val = df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else 'Missing'
                            df_cleaned[col] = df_cleaned[col].fillna(mode_val)
                            logs.append(
                                f"? Columna **'{col}'**: Valores vac�os/nulos de texto imputados con la moda ('{mode_val}').")

                # --- E. Saneamiento de Negativos ---
                for col in df_cleaned.select_dtypes(include=np.number).columns:
                    negative_mask = df_cleaned[col] < 0
                    negative_count = negative_mask.sum()
                    if negative_count > 0:
                        median_non_negative = df_cleaned[df_cleaned[col] >= 0][col].median()
                        if pd.isna(median_non_negative):
                            median_non_negative = df_cleaned[col].median()
                        df_cleaned.loc[negative_mask, col] = median_non_negative
                        logs.append(
                            f"? Columna **'{col}'**: {negative_count} valores negativos corregidos a la mediana positiva ({median_non_negative}).")

                # --- F. Organizaci�n de Texto y Ortograf�a ---
                for col in df_cleaned.select_dtypes(include=['object']).columns:
                    if df_cleaned[col].notna().any():
                        df_cleaned[col] = df_cleaned[col].astype(str)
                        if 'municipio' in col.lower() or 'departamento' in col.lower():
                            medellin_variations = ['Medell�n', 'Medellin', 'medell�n', 'MEDELLIN', 'MEdellin']
                            for var in medellin_variations:
                                df_cleaned[col] = df_cleaned[col].str.replace(var, 'Medell�n', case=False, regex=False)
                        df_cleaned[col] = df_cleaned[col].str.strip().str.title()

                # Guardar en el estado de la sesi�n
                st.session_state['df_cleaned'] = df_cleaned
                st.session_state['logs'] = logs
                st.success("? �Proceso de limpieza completado de forma exitosa!")

        # 4. Presentaci�n de Resultados y Descarga
        if 'df_cleaned' in st.session_state:
            df_final = st.session_state['df_cleaned']
            logs_finales = st.session_state['logs']

            st.write("---")
            st.subheader("? Reporte de Cambios Ejecutados")
            if logs_finales:
                for log in logs_finales:
                    st.markdown(log)
            else:
                st.write("El dataset estaba limpio. No se requirieron modificaciones estructurales.")

            st.subheader("? Vista Previa del Dataset Limpio")
            st.dataframe(df_final.head(10), use_container_width=True)
            st.caption(f"Dimensiones finales: {df_final.shape[0]} filas y {df_final.shape[1]} columnas.")

            # --- Generaci�n de Visualizaciones (EDA Autom�tico en Streamlit) ---
            st.subheader("? An�lisis Exploratorio de Datos Autom�tico (EDA)")

            numerical_cols = df_final.select_dtypes(include=np.number).columns
            categorical_cols = df_final.select_dtypes(include=['object']).columns

            if not numerical_cols.empty:
                st.markdown("**Distribuci�n de Variables Num�ricas:**")
                for col in numerical_cols:
                    fig, ax = plt.subplots(figsize=(7, 3))
                    sns.histplot(df_final[col], kde=True, ax=ax, color='#1f77b4')
                    ax.set_title(f'Distribuci�n de {col}')
                    st.pyplot(fig)
                    plt.close(fig)

            if not categorical_cols.empty:
                st.markdown("**Top Frecuencias de Variables Categ�ricas (Top 10):**")
                for col in categorical_cols:
                    top_10 = df_final[col].value_counts().nlargest(10)
                    if not top_10.empty:
                        fig, ax = plt.subplots(figsize=(8, 4))
                        sns.barplot(x=top_10.index, y=top_10.values, palette='viridis', ax=ax)
                        ax.set_title(f'Top 10 Valores en {col}')
                        plt.xticks(rotation=45, ha='right')
                        st.pyplot(fig)
                        plt.close(fig)

            if len(numerical_cols) > 1:
                st.markdown("**Matriz de Correlaci�n Num�rica:**")
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(df_final[numerical_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
                st.pyplot(fig)
                plt.close(fig)

            # --- Bot�n de Descarga Directa ---
            st.write("---")
            st.subheader("? Descargar Archivo Limpio")


            @st.cache_data
            def convert_df(df_to_convert):
                return df_to_convert.to_csv(index=False).encode('utf-8')


            csv_bytes = convert_df(df_final)
            base_name = os.path.splitext(uploaded_file.name)[0]

            st.download_button(
                label="? Descargar Dataset Limpio (CSV)",
                data=csv_bytes,
                file_name=f"{base_name}_limpio.csv",
                mime="text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Ocurri� un error general al procesar el archivo: {e}")
