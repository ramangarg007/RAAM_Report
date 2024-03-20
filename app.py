import streamlit as st
import pandas as pd
import numpy as np
# import altair as alt
import plotly.express as px

st.set_page_config(layout="wide")
st.title('RAAM Analysis')
st.sidebar.header('Filter Parameters')

st.subheader('File Upload')
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name='Data')
    st.write("filename:", uploaded_file.name)

else:
    df = pd.read_excel('./New Student - Transfer RAAM Report_Updated.xlsx', sheet_name='Data')


df = df.sort_values('Date')
# df = df.replace(to_replace='nan', value=np.nan)

filter_parameters = ['Status', 'Count', 'Student Type', 'Term Type']
plot_params = df.drop(['Date', 'Aid Year'] + filter_parameters, axis=1).columns


############### sidebar details section ###############

# status filter
Available_Status = tuple(df['Status'].unique())
status_type = st.sidebar.radio(
        "Status",
        Available_Status
    )


# count filter
Available_Count = tuple(df['Count'].unique())
count_type = st.sidebar.radio(
        "Count",
        Available_Count
    )


# Student Type
Available_Student_Type = tuple(df['Student Type'].unique())
student_type = st.sidebar.radio(
        "Student Type",
        Available_Student_Type
    )


# Term Type
Available_Term_Type = tuple(df['Term Type'].unique())
term_type = st.sidebar.radio(
        "Term Type",
        Available_Term_Type
    )

############### sidebar details section ###############

# Available_Status = tuple(df['Status'].unique())
# status_type = st.sidebar.radio(
#         "Status",
#         Available_Status
#     )


st.subheader('Plot Parameter')
plot_option = st.selectbox(
    'Parameter to Plot?',
    tuple(plot_params))

st.write('You selected:', plot_option)


# core logic

def get_week_name(date):
    # month = date.strftime('%B')
    week_number = (date.day - 1) // 7 + 1
    return week_number

df['week'] = df['Date'].dt.strftime('%U').astype(int)
df['year'] = df['Date'].dt.year
df['week_of_month'] = df['Date'].apply(get_week_name)
df['week_of_year'] = df['Date'].dt.strftime('%U').astype(int)
df['month'] = df['Date'].dt.strftime('%b')



df = df[(df['Status'] == status_type) & (df['Count'] == count_type) & (df['Student Type'] == student_type) & (df['Term Type'] == term_type)]


df_grouped = df.groupby(['Aid Year', 'month', 'week_of_year', 'week_of_month'], as_index=False)[plot_option].mean()
df_grouped['month_week_format'] = df_grouped['month'].astype(str) + ' ' + df_grouped['week_of_year'].astype(str)
df_grouped['required_format_week_month'] = df_grouped['month'].astype(str) + ' Week ' + df_grouped['week_of_month'].astype(str)
df_grouped = df_grouped.sort_values('week_of_year')
# df_grouped[:5]
# df_grouped = df_grouped.sort_values('week')

fig1 = px.scatter(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
             labels={plot_option: plot_option, 'week_of_year': 'Week', 'year': 'Year'},
             width=1400, height=400, color_discrete_sequence=px.colors.qualitative.G10)
fig1.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

fig2 = px.line(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
             labels={plot_option: plot_option, 'week_of_year': 'Week', 'year': 'Year'},
             width=1400, height=400, color_discrete_sequence=px.colors.qualitative.G10)
fig2.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

# fig2 = px.line(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
#              labels={plot_option: plot_option, 'week': 'Week', 'year': 'Year', 'month': 'month'},
#              title='Weekly Total Admit Count Over Years')
# fig.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

# fig2.update_xaxes(ticktext=df_grouped['required_format_week_month'].unique(),
#                   tickvals=df_grouped['week_of_year'].unique(), tickangle=90)
# fig2.update_layout(xaxis_title='Month/Week')
# fig.show()

st.subheader('Weekly {t} Over Years'.format(t=plot_option))
st.plotly_chart(fig1, use_container_width=True)


st.subheader('Weekly {t} Over Years'.format(t=plot_option))
st.plotly_chart(fig2, use_container_width=True)
