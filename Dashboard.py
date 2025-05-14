from matplotlib_venn import venn2

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk


df = pd.read_csv('dataset.csv')

st.markdown("<h1 style='text-align: center;'>Jurusan SAINTEK di Perguruan Tinggi Negri yang Sepi Peminat Namum Memiliki Prospek Kerja yang Baik</h1>", unsafe_allow_html=True)

st.subheader("Kelompok 10 C - Junior Data Scientist")
st.write("543_Ida Bagus Rahadi Putra")
st.write("545_Kadek Bakti Pramanayoga St")
st.write("546_Kadek Bisma Dharmasena")
st.write("548_Lusia Elvira Sue Sare")
st.divider()

# Statistics
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Jumlah PTN", value=df['Nama PTN'].nunique())
col2.metric(label="Jumlah Jurusan", value=df['Jurusan'].nunique())
col3.metric(label="Daya Tampung", value=df['Daya Tampung'].sum())
col4.metric(label="Peminat", value=df['Peminat'].sum())


st.subheader("Peta Persebaran Rasio Peminatan Jurusan SAINTEK Perguruan Tinggi Negri di Indonesia")
provinsi_coords = {
    "Sumatera Utara": (2.1154, 99.5451),
    "Sumatera Barat": (-0.7399, 100.8000),
    "Sumatera Selatan": (-3.3194, 104.9144),
    "Jawa Barat": (-6.9039, 107.6186),
    "Jawa Tengah": (-7.1500, 110.1403),
    "Yogyakarta": (-7.7956, 110.3695),
    "Jawa Timur": (-7.5361, 112.2384),
    "Kalimantan Barat": (0.1323, 111.0960),
    "Kalimantan Timur": (0.5383, 116.4194),
    "Kalimantan Selatan": (-3.0926, 115.2838),
    "Bali": (-8.4095, 115.1889),
    "NTB": (-8.6529, 117.3616),
    "NTT": (-9.4600, 119.8801),
    "Sulawesi Utara": (1.4931, 124.8413),
    "Sulawesi Tengah": (-1.4300, 121.4456),
    "Sulawesi Tenggara": (-4.0833, 122.5167),
    "Sulawesi Selatan": (-3.6688, 119.9741),
    "Maluku": (-3.2385, 130.1453),
    "Papua": (-4.2699, 138.0804),
    "Papua Selatan": (-7.5000, 139.6000)  # estimasi untuk provinsi baru
}

# Fungsi untuk ambil koordinat dari provinsi
def get_lat(prov):
    return provinsi_coords.get(prov, (None, None))[0]

def get_lon(prov):
    return provinsi_coords.get(prov, (None, None))[1]

# Terapkan ke dataframe
df['lat'] = df['Provinsi'].apply(get_lat)
df['lon'] = df['Provinsi'].apply(get_lon)

# Hitung warna (semakin rendah rasio makin merah, semakin tinggi makin hijau)
def rasio_to_color(rasio):
    g = min(int(rasio * 25), 255)
    r = 255 - g
    return [r, g, 100, 160]

df["color"] = df["Rasio Peminat"].apply(rasio_to_color)
df["radius"] = df["Rasio Peminat"] / df["Rasio Peminat"].max() * 150000

# Konversi ke dict agar dipakai pydeck
chart_data = df[["lat", "lon", "Nama PTN", "Jurusan", "Rasio Peminat", "color", "radius"]].dropna()
chart_data_dict = chart_data.to_dict(orient="records")

# Visualisasi dengan Pydeck
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=chart_data["lat"].mean(),
            longitude=chart_data["lon"].mean(),
            zoom=4,
            pitch=40,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=chart_data_dict,
                get_position="[lon, lat]",
                get_color="color",
                get_radius="radius",
                pickable=True,
                auto_highlight=True,
            )
        ],
        tooltip={
            "text": "PTN: {Nama PTN}\nJurusan: {Jurusan}\nRasio: {Rasio Peminat}"
        }
    )
)

st.divider()

# Top 10 Perguruan Tinggi Negri dengan Daya Tampung Tertinggi
st.subheader("Top 10 Perguruan Tinggi Negeri dengan Daya Tampung Terbanyak")
top_ptn_daya_tampung = df.groupby('Nama PTN')['Daya Tampung'].sum().reset_index()
top_ptn_daya_tampung = top_ptn_daya_tampung.sort_values(by='Daya Tampung', ascending=False).head(10)

fig = px.bar(
    top_ptn_daya_tampung,
    x='Nama PTN',
    y='Daya Tampung',
    text='Daya Tampung',
    color='Nama PTN'
)

fig.update_layout(
    xaxis_tickangle=-30,
    height=450,
    width=800,
    showlegend=False
)

st.plotly_chart(fig)



# Top 10 Sepi Peminat
st.subheader("Top 10 Jurusan di Perguruan Tinggi Negeri Sepi Peminat")

top_10_sepi_peminat = df.sort_values(by='Rasio Peminat', ascending=True).head(10)
top_10_sepi_peminat['Jurusan_PT'] = top_10_sepi_peminat['Jurusan'] + " - " + top_10_sepi_peminat['Nama PTN']

# Plot
fig = px.bar(
    top_10_sepi_peminat,
    x='Jurusan_PT',
    y='Rasio Peminat',
    hover_data=['Jurusan', 'Nama PTN', 'Rasio Peminat'],
)

# Atur label miring & tinggi grafik
fig.update_layout(
    height=450,
    width=800,
    xaxis_tickangle=-30,
)

st.plotly_chart(fig)

# Top 10 Jurusan dengan Prospek Kerja Baik berdasarkan Gaji
st.subheader("Top 10 Jurusan dengan Prospek Kerja Baik berdasarkan Rata-rata Gaji")
top_10_gaji = df.groupby('Jurusan')['Gaji'].mean().reset_index()
top_10_gaji = top_10_gaji.sort_values(by='Gaji', ascending=False).head(10)

fig = px.bar(
    top_10_gaji,
    x='Jurusan',
    y='Gaji',
    color='Jurusan'
)

fig.update_layout(
    xaxis_tickangle=-30,
    height=450,
    width=800,
    showlegend=False
)

st.plotly_chart(fig)

st.subheader("Venn Diagram Jurusan Sepi Peminat dan Prospek Kerja Baik")
# Set A: Rasio Peminat ≤ 2.63
set_rasio = set(df[df['Rasio Peminat'] <= 2.63]['Jurusan'] + " - " + df['Nama PTN'])

# Set B: Gaji ≥ 3.100.000
set_gaji = set(df[df['Gaji'] >= 3100000]['Jurusan'] + " - " + df['Nama PTN'])

# Hitung irisan dan buat plot
plt.figure(figsize=(6,6))
venn2([set_rasio, set_gaji], set_labels=('Jurusan Sepi Peminat', 'Prospek Kerja Baik'))

# Tampilkan di Streamlit
st.pyplot(plt)

choice = st.selectbox(
    "Melihat Detail Jurusan:",
    ("Sepi Peminat Prospek Kerja Tidak Baik", "Sepi Peminat Prospek Kerja Baik", "Rame Peminat Prospek Kerja Baik")
)
def show_set_as_table(set_data, title="Hasil"):
    if set_data:
        # Pastikan semua elemen adalah string
        cleaned = [str(item) for item in set_data]
        df_result = pd.DataFrame(sorted(cleaned), columns=["Jurusan - PTN"])
        st.subheader(title)
        st.dataframe(df_result)
    else:
        st.info("Tidak ada jurusan yang memenuhi kriteria.")

if choice == "Sepi Peminat Prospek Kerja Tidak Baik":
    show_set_as_table(set_rasio - set_gaji, "Sepi Peminat & Prospek Kerja Tidak Baik")
elif choice == "Sepi Peminat Prospek Kerja Baik":
    show_set_as_table(set_rasio & set_gaji, "Sepi Peminat & Prospek Kerja Baik")
elif choice == "Rame Peminat Prospek Kerja Baik":
    show_set_as_table(set_gaji - set_rasio, "Rame Peminat & Prospek Kerja Baik")