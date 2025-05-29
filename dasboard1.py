# filepath: e:\python_projects\Streamlit_Interactive_Dashboard\dashboard.py
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import csv
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Superstore!!",page_icon=':bar_chart:', layout="wide")

st.title(' :bar_chart: Superstore Sales EDA')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

f1 = st.file_uploader(":file_upload: Upload a file", type=(["csv","xlsx","xls","txt"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    file_extension = filename.split('.')[-1].lower()  # Extract file extension

    if file_extension in ['csv', 'txt']:
        try:
            df = pd.read_csv(filename, encoding='ISO-8859-1', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            df = None  # or handle the error as appropriate
    elif file_extension in ['xls', 'xlsx']:
        try:
            df = pd.read_excel(filename)
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            df = None # or handle the error as appropriate
    else:
        st.error("Unsupported file type. Please upload a CSV, TXT, XLS, or XLSX file.")
        df = None

else:
    try:
        os.chdir(r"E:\python_projects\Streamlit_Interactive_Dashboard")
        df = pd.read_excel("Superstore.xls") # Assuming it's Excel
    except Exception as e:
        st.error(f"Error reading default Excel file: {e}")
        df = None


col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# Getting the min max date
startdate = pd.to_datetime(df['Order Date'].min())
enddate = pd.to_datetime(df['Order Date'].max())


with col1:
    date1 =pd.to_datetime(st.date_input("Start Date", startdate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", enddate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect('Pick your Region',df['Region'].unique())

# create for region

if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

# create for state
state = st.sidebar.multiselect('Pick your State', df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

# create for city
city = st.sidebar.multiselect('Pick your City', df3['City'].unique())

# filter the data based on region, state, and city
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif state and city:
    filtered_df = df3[df['State'].isin(state) & df3['City'].isin(city)]

elif region and city:
    filtered_df = df3[df['Region'].isin(region) & df3['City'].isin(city)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df3['State'].isin(state)]

elif city:
    filtered_df = df3[df['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]

category_df = filtered_df.groupby(by = ['Category'], as_index = False)['Sales'].sum()

with col1:
    st.subheader('Category wise Sales')
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text= ['${:,.2f}'.format(x) for x in category_df['Sales']],
                 template= 'seaborn')
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
    st.subheader('Region wise Sales')
    fig = px.pie(filtered_df, names='Region', values='Sales',hole=0.5)
    fig.update_traces(text = filtered_df['Region'], textposition = 'outside')
    st.plotly_chart(fig, use_container_width=True, height = 200)
