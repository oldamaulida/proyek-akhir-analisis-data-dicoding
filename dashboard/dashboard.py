import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_charter_df(df):  #bertanggung jawab menyiapkan create_daily_charter
    daily_charter_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    daily_charter_df = daily_charter_df.reset_index()
    daily_charter_df.rename(columns={
        "instant": "tenant_count",
        "cnt": "revenue"
    }, inplace=True)
    
    return daily_charter_df

def create_sum_charter_items_df(df):  #bertanggung jawab menyiapkan sum_charter_items
    sum_charter_items_df = df.groupby("instant").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_charter_items_df

def create_byworkingday_df(df):  #bertanggung jawab menyiapkan byworkingday_df
    byworkingday_df = df.groupby(by="workingday").instant.nunique().reset_index()
    byworkingday_df.rename(columns={
        "instant": "tenant_count"
    }, inplace=True)
    
    return byworkingday_df

def create_byyr_df(df): #bertanggung jawab menyiapkan byyear_df
    byyr_df = df.groupby(by="yr").instant.nunique().reset_index()
    byyr_df.rename(columns={
        "instant":"tenant_count"
    }, inplace=True)

    return byyr_df

def create_rfm_df(df):  #bertanggung jawab menyiapkan rfm_df
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max", #mengambil tanggal order terakhir
        "cnt": ["nunique", "sum"]
    })
    rfm_df.columns = ["instant", "max_tenant_timestamp", "frequency", "monetary"]
    
    rfm_df["max_tenant_timestamp"] = rfm_df["max_tenant_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_tenant_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_tenant_timestamp", axis=1, inplace=True)
    
    return rfm_df

day_bk = pd.read_csv("https://raw.githubusercontent.com/oldamaulida/proyek-akhir-analisis-data-dicoding/main/dashboard/fix_data.csv")
#mengurutkan data frame berdasarkan datetime
datetime_columns = ["dteday"]
day_bk.sort_values(by="dteday", inplace=True)
day_bk.reset_index(inplace=True)
 
for column in datetime_columns:
    day_bk[column] = pd.to_datetime(day_bk[column])
min_date = day_bk["dteday"].min()
max_date = day_bk["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/oldamaulida/proyek-akhir-analisis-data-dicoding/main/dashboard/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_bk[(day_bk["dteday"] >= str(start_date)) & 
                (day_bk["dteday"] <= str(end_date))]

daily_charter_df = create_daily_charter_df(main_df)
sum_charter_items_df = create_sum_charter_items_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byyr_df = create_byyr_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Charter Bicycle Dashboard :sparkles:')

# menampilkan tiga informasi terkait daily sharing, yaitu jumlah tenant dan jumlah sharing
st.subheader('Daily Charter')
 
col1, col2 = st.columns(2)
 
with col1:
    total_cust = daily_charter_df.tenant_count.sum()
    st.metric("Total Tenant", value=total_cust)
 
with col2:
    total_revenue = format_currency(daily_charter_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_charter_df["dteday"],
    daily_charter_df["revenue"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Menampilkan pola perbedaan peminjaman sepeda antara hari libur dan hari kerja
st.subheader("Differences in Bicycle Charter Patterns between Holidays and Weekdays")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(35, 20))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x='workingday', y='cnt', data=day_bk)
ax.set_ylabel('Total Rental Bikes (cnt)', fontsize=30)
ax.set_xlabel('Working Day (0: Holiday, 1: Working Day)', fontsize=30)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# memasukkan 2 buah visualisasi data ke dalam dashboard
st.subheader("Tenant Demographics")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 15))
    
    colors = ["#D3D3D3", "#90CAF9", "#A7F9EA", "#FDD2FC", "#FBF7D3"]

    sns.barplot(
        y="tenant_count", 
        x="yr",
        data=byyr_df.sort_values(by="tenant_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Tenant by Year (2011 & 2012)", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(20, 15))
    
    colors = ["#D3D3D3", "#90CAF9", "#A7F9EA", "#FDD2FC", "#FBF7D3"]

    sns.barplot(
        y="tenant_count", 
        x="workingday",
        data=byworkingday_df.sort_values(by="tenant_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Tenant by Workingday", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# menampilkan nilai average atau rata-rata dari ketiga parameter tersebut menggunakan widget metric()
# menampilkan hasil visualisasi data dari latihan sebelumnya
st.subheader("Best Tenant Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df.monetary.mean(), 3) 
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("instant", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("instant", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="instant", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("instant", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright (c) Bicycle Analysis 2024')