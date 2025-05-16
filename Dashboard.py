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

st.subheader("Statistik Deskriptif Data")
st.write(df.describe())
st.markdown("""**Penjelasan**:
            
**Rasio Peminat** menunjukkan perbandingan antara jumlah peminat dengan daya tampung. Nilai rata-ratanya adalah **2.63**, artinya secara umum, tiap kursi jurusan diincar oleh 2–3 orang. Oleh karena itu, **ambang batas 2.63** digunakan untuk menentukan jurusan "Sepi Peminat", karena berada tepat di nilai **rata-rata**, sehingga jurusan di bawah rata-rata ini dianggap sepi peminat secara statistik.
""")
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

# Top 10 Perguruan Tinggi Negri dengan Daya Tampung Tertinggi/Terendah
daya_tampung = st.selectbox("Pilih Filter:", ("Tertinggi", "Terendah"))
if daya_tampung == "Tertinggi":
    st.subheader("Top 10 Perguruan Tinggi Negeri dengan Daya Tampung Tertinggi")
    top_ptn_daya_tampung = df.groupby('Nama PTN')['Daya Tampung'].sum().reset_index()
    top_ptn_daya_tampung = top_ptn_daya_tampung.sort_values(by='Daya Tampung', ascending=False).head(10)
else:
    st.subheader("Top 10 Perguruan Tinggi Negeri dengan Daya Tampung Terendah")
    top_ptn_daya_tampung = df.groupby('Nama PTN')['Daya Tampung'].sum().reset_index()
    top_ptn_daya_tampung = top_ptn_daya_tampung.sort_values(by='Daya Tampung', ascending=True).head(10)

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

if daya_tampung == "Tertinggi":
    st.markdown(f"""**Insight**
- Perguruan Tinggi Negeri dengan daya tampung tertinggi adalah **{top_ptn_daya_tampung.iloc[0]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[0]['Daya Tampung']}**.
- Daya tampung tertinggi kedua adalah **{top_ptn_daya_tampung.iloc[1]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[1]['Daya Tampung']}**.
- Daya tampung tertinggi ketiga adalah **{top_ptn_daya_tampung.iloc[2]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[2]['Daya Tampung']}**.
""")
else:
    st.markdown(f"""**Insight**
- Perguruan Tinggi Negeri dengan daya tampung terendah adalah **{top_ptn_daya_tampung.iloc[0]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[0]['Daya Tampung']}**.
- Daya tampung terendah kedua adalah **{top_ptn_daya_tampung.iloc[1]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[1]['Daya Tampung']}**.
- Daya tampung terendah ketiga adalah **{top_ptn_daya_tampung.iloc[2]['Nama PTN']}** dengan daya tampung **{top_ptn_daya_tampung.iloc[2]['Daya Tampung']}**.
""")

st.divider()

# Top 10 Sepi Peminat/Rame Peminat
peminat = st.selectbox("Pilih Filter:", ("Sepi Peminat", "Rame Peminat"))
if peminat == "Sepi Peminat":
    st.subheader("Top 10 Jurusan di Perguruan Tinggi Negeri Sepi Pemininat")
    top_10_peminat = df.sort_values(by='Rasio Peminat', ascending=True).head(10)
    top_10_peminat['Jurusan_PT'] = top_10_peminat['Jurusan'] + " - " + top_10_peminat['Nama PTN']
else:
    st.subheader("Top 10 Jurusan di Perguruan Tinggi Negeri Rame Peminat")
    top_10_peminat = df.sort_values(by='Rasio Peminat', ascending=False).head(10)
    top_10_peminat['Jurusan_PT'] = top_10_peminat['Jurusan'] + " - " + top_10_peminat['Nama PTN']

# Plot
fig = px.bar(
    top_10_peminat,
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

if peminat == "Sepi Peminat":
    st.markdown(f"""**Insight**
- Jurusan dengan rasio peminat terendah adalah **{top_10_peminat.iloc[0]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[0]['Rasio Peminat']}**.
- Jurusan dengan rasio peminat terendah kedua adalah **{top_10_peminat.iloc[1]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[1]['Rasio Peminat']}**.
- Jurusan dengan rasio peminat terendah ketiga adalah **{top_10_peminat.iloc[2]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[2]['Rasio Peminat']}**.
""")
else:
    st.markdown(f"""**Insight**
- Jurusan dengan rasio peminat tertinggi adalah **{top_10_peminat.iloc[0]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[0]['Rasio Peminat']}**.
- Jurusan dengan rasio peminat tertinggi kedua adalah **{top_10_peminat.iloc[1]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[1]['Rasio Peminat']}**.
- Jurusan dengan rasio peminat tertinggi ketiga adalah **{top_10_peminat.iloc[2]['Jurusan_PT']}** dengan rasio peminat **{top_10_peminat.iloc[2]['Rasio Peminat']}**.
""")

st.divider()

# Top 10 Jurusan dengan Prospek Kerja Baik berdasarkan Gaji
st.subheader("Top 10 Jurusan dengan Prospek Kerja Baik berdasarkan Rata-rata Gaji")
top_10_gaji = df.groupby('Jurusan')['Gaji'].mean().reset_index()
top_10_gaji = top_10_gaji.sort_values(by='Gaji', ascending=False).head(10)
prospek_kerja_baik = df.groupby('Jurusan')['Gaji'].mean().reset_index()
prospek_kerja_baik = prospek_kerja_baik.sort_values(by='Gaji', ascending=False)
prospek_kerja_baik = prospek_kerja_baik[prospek_kerja_baik['Gaji'] >= 3100000]

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

st.markdown(f"""**Insight**
- Berdasarkan data dari Badan Pusat Statistik (BPS) tahun 2025, rata-rata gaji di Indonesia adalah **Rp 3.100.000**. Oleh karena itu, jurusan dengan gaji di atas rata-rata adalah dianggap memiliki prospek kerja yang baik. Sumber: [BPS](https://www.bps.go.id/id/statistics-table/2/MTUyMSMy/rata-rata-upah-gaji.html).
- Jurusan dengan rata-rata gaji tertinggi adalah **{top_10_gaji.iloc[0]['Jurusan']}** dengan rata-rata gaji **Rp {"{:,.2f}".format(top_10_gaji.iloc[0]['Gaji']).replace(",", "X").replace(".", ",").replace("X", ".")}**.
- Jurusan dengan rata-rata gaji tertinggi kedua adalah **{top_10_gaji.iloc[1]['Jurusan']}** dengan rata-rata gaji **Rp {"{:,.2f}".format(top_10_gaji.iloc[1]['Gaji']).replace(",", "X").replace(".", ",").replace("X", ".")}**.
- Jurusan dengan rata-rata gaji tertinggi ketiga adalah **{top_10_gaji.iloc[2]['Jurusan']}** dengan rata-rata gaji **Rp {"{:,.2f}".format(top_10_gaji.iloc[2]['Gaji']).replace(",", "X").replace(".", ",").replace("X", ".")}**.
""")

st.divider()

# Venn Diagram
st.subheader("Venn Diagram Jurusan Sepi Peminat dan Prospek Kerja Baik")

# Bersihkan baris yang memiliki NaN di Jurusan atau Nama PTN
df_clean = df.dropna(subset=['Jurusan', 'Nama PTN'])

# Set A: Rasio Peminat ≤ 2.63
set_rasio = set(
    df_clean[df_clean['Rasio Peminat'] <= 2.63]
    .apply(lambda row: f"{row['Jurusan']} - {row['Nama PTN']}", axis=1)
)

# Set B: Gaji ≥ 3.100.000
set_gaji = set(
    df_clean[df_clean['Gaji'] >= 3100000]
    .apply(lambda row: f"{row['Jurusan']} - {row['Nama PTN']}", axis=1)
)

# Hitung irisan dan buat plot
plt.figure(figsize=(6, 6))
venn2([set_rasio, set_gaji], set_labels=('Jurusan Sepi Peminat', 'Prospek Kerja Baik'))

# Tampilkan di Streamlit
st.pyplot(plt)

# Pilihan analisis kombinasi
choice = st.selectbox(
    "Melihat Detail Jurusan:",
    (
        "Sepi Peminat Prospek Kerja Kurang Baik",
        "Sepi Peminat Prospek Kerja Baik",
        "Rame Peminat Prospek Kerja Baik"
    )
)

# Fungsi tampilkan set ke tabel
def show_set_as_table(set_data, title="Hasil"):
    if set_data:
        cleaned = [str(item) for item in set_data]
        df_result = pd.DataFrame(sorted(cleaned), columns=["Jurusan - PTN"])
        st.subheader(title)
        st.dataframe(df_result)
    else:
        st.info("Tidak ada jurusan yang memenuhi kriteria.")

# Logika pilihan
if choice == "Sepi Peminat Prospek Kerja Kurang Baik":
    show_set_as_table(set_rasio - set_gaji, "Sepi Peminat & Prospek Kerja Kurang Baik")
elif choice == "Sepi Peminat Prospek Kerja Baik":
    show_set_as_table(set_rasio & set_gaji, "Sepi Peminat & Prospek Kerja Baik")
elif choice == "Rame Peminat Prospek Kerja Baik":
    show_set_as_table(set_gaji - set_rasio, "Rame Peminat & Prospek Kerja Baik")

st.markdown("""**Insight**
- Jurusan yang sepi peminat dan memiliki prospek kerja baik adalah jurusan yang memiliki rasio peminat di bawah **2.63** dan gaji di atas **Rp 3.100.000**. Pada diagram Venn, area irisan antara dua lingkaran menunjukkan jurusan yang memenuhi kedua kriteria tersebut dengan total 73 Jurusan.
- Jurusan yang sepi peminat dan memiliki prospek kerja kurang baik adalah jurusan yang memiliki rasio peminat di bawah **2.63** dan gaji di bawah **Rp 3.100.000**. Pada diagram Venn, area luar lingkaran kiri menunjukkan jurusan yang memenuhi kedua kriteria tersebut dengan total 4 Jurusan.
- Jurusan yang rame peminat dan memiliki prospek kerja baik adalah jurusan yang memiliki rasio peminat di atas **2.63** dan gaji di atas **Rp 3.100.000**. Pada diagram Venn, area luar lingkaran kanan menunjukkan jurusan yang memenuhi kedua kriteria tersebut dengan total 32 Jurusan.
""")