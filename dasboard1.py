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


cl1, cl2 = st.columns(2)

with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Category Data",
            data=csv,
            file_name='category_data.csv',
            mime='text/csv',
            help="Click here to download the data as a CSV file."
            )
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by=['Region'], as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Region Data",
            data=csv,
            file_name='region_data.csv',
            mime='text/csv',
            help="Click here to download the data as a CSV file."
        )

filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y:%b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x='month_year', y='Sales', labels={'Sales': 'Amount'},height=500, width=1000,template='gridon')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time series"):
    st.write(linechart.T.style.background_gradient(cmap='Greens'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Time Series Data",
        data=csv,
        file_name='time_series_data.csv',
        mime='text/csv',
        help="Click here to download the data as a CSV file."
    )
# Create a treemap based on Region, category , sub-category
st.subheader('Hierarchical view of sales using TreeMap')
fig3 = px.treemap(filtered_df, path=['Region', 'Category', 'Sub-Category'], values='Sales', hover_data=['Sales'],
                  color= 'Sub-Category')
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)


