# Install library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Membaca dataset
df = pd.read_csv('mall_customers.csv')

# Menampilkan nama kolom asli untuk memastikan tidak ada kesalahan ejaan
st.write("Kolom dalam dataset sebelum rename:", df.columns)

# Rename kolom agar lebih mudah digunakan
df = df.rename(columns={
    'Annual Income (k$)': 'Income',  # Perbaiki jika salah ejaan
    'Spending Score (1-100)': 'Score'
})

# Menampilkan nama kolom setelah rename
st.write("Kolom dalam dataset setelah rename:", df.columns)

# Menghapus kolom yang tidak digunakan
X = df.drop(['CustomerID', 'Gender'], axis=1)

# Menampilkan dataset di Streamlit
st.header("Isi Dataset")
st.write(df)

# **Elbow Method untuk Menentukan K Optimal**
clusters = []
for i in range(1, 11):
    km = KMeans(n_clusters=i, random_state=42).fit(X)
    clusters.append(km.inertia_)

# Membuat plot elbow method
fig, ax = plt.subplots(figsize=(12, 8))  # Perbaikan dari plt.subplot()
sns.lineplot(x=list(range(1, 11)), y=clusters, ax=ax)
ax.set_title('Menentukan Elbow Method')
ax.set_xlabel('Jumlah Clusters')
ax.set_ylabel('Inertia')

# Anotasi elbow point (bisa disesuaikan dengan hasil grafik)
ax.annotate('Possible elbow point', xy=(3, clusters[2]), xytext=(3, max(clusters) * 0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3', color='blue', lw=2))

ax.annotate('Possible elbow point', xy=(5, clusters[4]), xytext=(5, max(clusters) * 0.8),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3', color='blue', lw=2))

# Menampilkan plot di Streamlit
st.pyplot(fig)

# **Menentukan jumlah cluster dengan slider di sidebar**
st.sidebar.subheader("Tentukan jumlah K (Cluster)")
clust = st.sidebar.slider("Pilih jumlah cluster:", 2, 10, 3, 1)

# **Fungsi untuk melakukan K-Means Clustering**
def k_means(n_clust):
    kmean = KMeans(n_clusters=n_clust, random_state=42).fit(X)
    X['Labels'] = kmean.labels_

    # Membuat scatter plot hasil clustering
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x=X['Income'], y=X['Score'], hue=X['Labels'], palette=sns.color_palette('hls', n_clust), s=100)

    # Menambahkan anotasi centroid
    for label in X['Labels'].unique():
        plt.annotate(label,
                     (X[X['Labels'] == label]['Income'].mean(),
                      X[X['Labels'] == label]['Score'].mean()),
                     horizontalalignment='center',
                     verticalalignment='center',
                     size=12, weight='bold',
                     color='black', backgroundcolor='white')
    
    plt.title("Cluster Plot K-Means")
    plt.xlabel("Income")
    plt.ylabel("Spending Score")

    # Menampilkan plot di Streamlit
    st.pyplot()
    st.write("Hasil Clustering:")
    st.write(X)

# Menjalankan fungsi clustering dengan nilai K dari slider
k_means(clust)
