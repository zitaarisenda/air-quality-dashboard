import streamlit as st
import gdown
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
import folium
from streamlit_folium import folium_static
from PIL import Image

url = "https://drive.google.com/uc?id=14RFUpJQN-H_9RY6O53_dCX0AoMeJHidy"
output = "air_quality_all.csv"

gdown.download(url, output, quiet=False)

# Load Data
df = pd.read_csv("air_quality_all.csv")

# Halaman Utama
st.title("Dashboard Kualitas Udara di China")
# ID file Google Drive
file_id = "1DOBoHaEYgnB7wHlW5C4YESLf3WiqOVZC"

# URL unduhan langsung
url = f"https://drive.google.com/uc?id={file_id}"

# Unduh file
output = "air_quality_bg.jpg"
gdown.download(url, output, quiet=False)

# Tampilkan gambar
image = Image.open("air_quality_bg.jpg")
st.image(image, use_container_width=True)

st.subheader("Preview Data")
st.dataframe(df.head())

def visualize_station_distribution(df):
    station_counts = df["station"].value_counts()
    labels = [f"{s}\n({c/sum(station_counts)*100:.1f}%, {c})" for s, c in zip(station_counts.index, station_counts)]
    colors = sns.color_palette("Oranges", len(station_counts))
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(station_counts, labels=labels, colors=colors, startangle=140)
    ax.set_title("Distribusi Data per Stasiun", fontsize=14)
    st.pyplot(fig)
    st.write("Distribusi data dari tiap stasiun cukup merata.")

def visualize_scatter_plots(df):
    st.subheader("Scatter Plots")

    # Ambil sampel acak (20% dari total data)
    df_sampled = df.sample(frac=0.2, random_state=42)

    # Daftar pasangan kolom yang akan diplot
    pairs = [
        ("TEMP", "PRES"),
        ("TEMP", "DEWP"),
        ("PRES", "DEWP"),
        ("PM2.5", "PM10")
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, (x_col, y_col) in enumerate(pairs):
        axes[i].scatter(df_sampled[x_col], df_sampled[y_col], alpha=0.5, s=10, color="orange")
        axes[i].set_xlabel(x_col)
        axes[i].set_ylabel(y_col)
        axes[i].set_title(f"{x_col} vs {y_col}")
        axes[i].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)
    st.write("Diambil sample secara acak sebesar 20% dari data agar visual scatter plot terbaca lebih jelas."
    "Pada scatter plot terlihat bahwa korelasi positif dimiliki pasangan TEMP vs DEWP dan PM2.5 vs PM10."
    "Sedangkan korelasi negatif dimiliki pasangan TEMP vs PRES dan PRES vs DEWP."
    "Dapat diambil kesimpulan bahwa kolom yang berpasangan memiliki ketergantungan/hubungan yang kuat karena scatter plot yang ditampilkan memiliki tingkat kemiringan sekitar 45 derajat.")

def show_monthly_averages(df):
    st.subheader("Data Kualitas Udara Berdasar Waktu")

    # Buat kolom 'year_month' dalam format YYYY-MM
    df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

    # Hitung rata-rata bulanan untuk parameter yang dipilih
    df_monthly = df.groupby("year_month").agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "CO": "mean",
        "O3": "mean",
        "NO2": "mean",
        "TEMP": "mean",
        "PRES": "mean",
        "DEWP": "mean",
        "RAIN": "mean",
        "WSPM": "mean"
    }).reset_index()

    st.dataframe(df_monthly) 

def visualize_map(df):
    pm25_mean = df.groupby("station")["PM2.5"].mean().to_dict()
    temp_mean = df.groupby("station")["TEMP"].mean().to_dict()

    locations = {
        "Aotizhongxin": (40.018, 116.397),
        "Changping": (40.220, 116.231),
        "Dingling": (40.292, 116.220),
        "Dongsi": (39.929, 116.417),
        "Guanyuan": (39.929, 116.339),
        "Gucheng": (39.912, 116.184),
        "Huairou": (40.322, 116.628),
        "Nongzhanguan": (39.933, 116.461),
        "Shunyi": (40.127, 116.654),
        "Tiantan": (39.882, 116.411),
        "Wanliu": (39.987, 116.303),
        "Wanshouxigong": (39.878, 116.339),
    }

    def get_color(pm25):
        if pm25 < 50:
            return "blue"
        elif pm25 < 55:
            return "yellow"
        elif pm25 < 60:
            return "orange"
        else:
            return "red"

    def get_size(pm25):
        if pm25 < 50:
            return 5
        elif pm25 < 55:
            return 10
        elif pm25 < 60:
            return 15
        else:
            return 20

    # Buat peta
    m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

    for station, (lat, lon) in locations.items():
        pm25 = pm25_mean.get(station, "No Data")
        temp = temp_mean.get(station, "No Data")

        if isinstance(pm25, (int, float)):
            color = get_color(pm25)
            size = get_size(pm25)
        else:
            color = "gray"
            size = 5 

        folium.CircleMarker(
            location=[lat, lon],
            radius=size,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"<b>{station}</b><br>Mean PM2.5: {pm25:.2f}<br>Mean TEMP: {temp:.2f}°C",
            tooltip=f"{station} (PM2.5: {pm25:.2f}, TEMP: {temp:.2f}°C)"
        ).add_to(m)

    folium_static(m)

    st.markdown("""
    - **PM2.5**: Partikulat halus berukuran ≤2.5 µm yang berbahaya karena dapat menembus paru-paru dan aliran darah sehingga menjadi indikator utama polusi udara.  
    - **TEMP**: Suhu udara dapat memengaruhi penyebaran dan konsentrasi polutan di atmosfer.
    """)

    st.write("Dalam map interaktif, stasiun diklastering menjadi 4 warna. Berikut kategori berdasarkan rata-rata PM2.5:")

    st.markdown("""
    - **Sangat tercemar (merah)** PM2.5 >= 60: Tiantan, Wanshouxigong, Dongsi, Gucheng, Guanyuan  
    - **Tercemar (oranye)** 55 <= PM2.5 < 60: Wanliu, Aotizhongxin, Nongzhanguan, Shunyi  
    - **Sedang (kuning)** 50 <= PM2.5 < 55: Changping, Huairou  
    - **Tidak tercemar (biru)** PM2.5 < 50: Dingling  
    """)

    st.write("Dapat diamati bahwa stasiun yang berada di pusat kota memiliki tingkat pencemaran dan polusi yang lebih tinggi dibandingkan stasiun yang jauh dari pusat kota.")

def visualize_scatter(df):
    df_grouped = df.groupby("station").agg({
        "PM2.5": ["mean", "median", "max", "min"],
        "PM10": ["mean", "median", "max", "min"],
        "NO2": ["mean", "median", "max", "min"]
    }).reset_index()

    df_grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df_grouped.columns]

    x = df_grouped["PM2.5_mean"]
    y = df_grouped["PM10_mean"]
    size = 600
    colors = df_grouped["NO2_mean"]

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(x, y, s=size, c=colors, cmap="spring", alpha=0.3, edgecolors="black", linewidths=0.3)

    cbar = plt.colorbar(scatter)
    cbar.set_label("Average NO2 Level")

    texts = []
    for i, station in enumerate(df_grouped["station"]):
        texts.append(plt.text(x[i], y[i], station, fontsize=9, ha="center", color="black"))

    adjust_text(texts, arrowprops=dict(arrowstyle="-", color="gray", lw=0.5))

    plt.xlabel('Average PM2.5')
    plt.ylabel('Average PM10')
    plt.title('Air Quality per Station (Colored by NO2 Level)')
    plt.grid(True, linestyle="--", alpha=0.5)

    st.pyplot(plt)

    st.markdown("""
    - **PM10**: Partikulat kasar berukuran ≤10 µm yang dapat menyebabkan masalah pernapasan serta sering digunakan untuk mengukur tingkat debu dan polutan di udara.  
    - **NO2**: Gas nitrogen dioksida yang berasal dari emisi kendaraan dan industri sering dikaitkan dengan kualitas udara yang buruk dan gangguan pernapasan.
    """)
    st.write("Dalam scatter plot terlihat bahwa stasiun dengan kadar PM2.5 yang tinggi juga memiliki kadar PM10 dan NO2 yang relatif tinggi. Berikut klaster berdasarkan rata-rata NO2:")

    st.markdown("""
    - **Sangat tinggi (kuning)** NO2 > 55: Wanliu  
    - **Tinggi (oranye)** 45 <= NO2 < 55: Tiantan, Dongsi, Wanshouxigong, Gucheng, Nongzhanguan, Guanyuan, Aotizhongxin  
    - **Sedang (krem)** 35 <= NO2 < 45: Changping, Shunyi  
    - **Rendah (pink)** NO2 < 35: Dingling, Huairou  
    """)

def visualize_wind_speed(df):
    # Filter hanya 3 arah mata angin yang diinginkan
    selected_wd = ["WNW", "NNW", "NW"]
    df_filtered = df[df["wd"].isin(selected_wd)].copy()

    # Format kolom "year_month" untuk agregasi
    df_filtered["year_month"] = df_filtered["year"].astype(str) + "-" + df_filtered["month"].astype(str).str.zfill(2)

    # Hitung rata-rata WSPM per tahun-bulan untuk setiap arah angin
    df_wd = df_filtered.groupby(["year_month", "wd"])["WSPM"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = {"WNW": "blue", "NW": "orange", "NNW": "green"}
    alphas = {"WNW": 1, "NW": 0.3, "NNW": 0.3}

    for wd in selected_wd:
        subset = df_wd[df_wd["wd"] == wd]
        ax.plot(subset["year_month"], subset["WSPM"], linestyle="-", linewidth=2,
                label=wd, color=colors[wd], alpha=alphas[wd])
        
    ax.set_xlabel("Year-Month")
    ax.set_ylabel("Average Wind Speed (WSPM)")
    ax.set_title("Average Wind Speed per Year-Month for Selected Wind Directions")
    ax.legend(title="Wind Direction")
    ax.grid(True, linestyle="--", alpha=0.5)

    ax.set_xticks(df_wd["year_month"][::6])
    ax.set_xticklabels(df_wd["year_month"][::6], rotation=45, fontsize=10)
    st.subheader("Wind Speed Analysis")
    st.pyplot(fig)
    st.write("Tiga mata angin terkuat yakni WNW (2.28), NW (2.27), dan NNW (2.06).")
    st.write("Dalam visualisasi terlihat bahwa kekuatan kecepatan angin memiliki pola berulang.")
    st.write("Pada periode September-April, kekuatan angin cenderung naik.")
    st.write("Sementara pada periode Mei-Agustus, kekuatan angin relatif turun.")
    st.write("Dalam grafik juga teramati bahwa kekuatan angin memiliki tren naik selama rentang tahun 2013-2017.")

def visualize_per_station(df):
    columns = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    stations = df["station"].unique()
    selected_station = st.sidebar.selectbox("Pilih Stasiun untuk Histogram", stations)
    df_station = df[df["station"] == selected_station]

    st.subheader(f"Data Stasiun {selected_station}")
    st.dataframe(df_station.head())

    st.subheader(f"Statistik Data untuk Stasiun {selected_station}")
    st.write(df_station.drop(columns=["No"], errors='ignore').describe())

    fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(15, 12))
    axes = axes.flatten()

    for i, col in enumerate(columns):
        ax = axes[i]
        mean_values = df_station.groupby("year")[col].mean()
        max_value = mean_values.max()
        colors = ["orange" if v == max_value else "yellow" for v in mean_values]
        mean_values.plot(kind="bar", ax=ax, color=colors, edgecolor="black")
        ax.set_title(f"Average {col} per Year")
        ax.set_xlabel("Year")
        ax.set_ylabel(col)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    if len(columns) < len(axes):
        fig.delaxes(axes[-1])
    
    plt.tight_layout()
    st.subheader(f"Histogram Rata-rata Indikator Kualitas Udara per Tahun - {selected_station}")
    st.pyplot(fig)
    st.write("Data untuk tahun 2017 menunjukkan visual yang berbeda dari tahun-tahun sebelumnya akibat keterbatasan data dari tahun 2017 (hanya bulan awal).")

    # Pie chart arah mata angin
    st.subheader(f"Distribusi Arah Mata Angin di Stasiun {selected_station}")
    wind_counts = df_station["wd"].value_counts()
    colors = sns.color_palette("Oranges", len(wind_counts))
    
    top_winds = wind_counts.nlargest(5)
    labels = wind_counts.index.tolist()
    autopct_labels = [f"{c/sum(wind_counts)*100:.1f}%" if w in top_winds.index else "" for w, c in zip(wind_counts.index, wind_counts)]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(wind_counts, labels=labels, colors=colors, startangle=140, autopct=lambda p: f'{p:.1f}%' if p > 0 else '')
    
    for i, t in enumerate(autotexts):
        if labels[i] not in top_winds.index:
            t.set_text("")
    
    st.pyplot(fig)


# Sidebar
st.sidebar.title("Menu")
menu = st.sidebar.radio("Pilih Analisis", ["Exploratory", "Analisa dan Visualisasi", "Visualisasi Interaktif Stasiun"])

if menu == "Exploratory":
    option = st.sidebar.selectbox("Pilih Visualisasi", ["Distribusi Stasiun", "Scatter Plots", "Kualitas Udara Berdasar Waktu"])
    if option == "Distribusi Stasiun":
        visualize_station_distribution(df)
    elif option == "Scatter Plots":
        visualize_scatter_plots(df)
    elif option == "Kualitas Udara Berdasar Waktu":
        show_monthly_averages(df)
elif menu == "Visualisasi Interaktif Stasiun":
    visualize_per_station(df)
elif menu == "Analisa dan Visualisasi":
    option = st.sidebar.selectbox("Pilih Analisis", ["Peta Stasiun", "Scatter Plot Stasiun", "Kecepatan Angin"])
    if option == "Peta Stasiun":
        visualize_map(df)
    elif option == "Scatter Plot Stasiun":
        visualize_scatter(df)
    elif option == "Kecepatan Angin":
        visualize_wind_speed(df)
