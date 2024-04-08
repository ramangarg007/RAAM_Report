import streamlit as st
import pandas as pd
import numpy as np
# import altair as alt
import plotly.express as px
import re

st.set_page_config(layout="wide")
st.title('RAAM Analysis')
st.sidebar.header('Filter Parameters')

st.subheader('File Upload')
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("filename:", uploaded_file.name)

else:
    df = pd.read_csv('./RAAM_REPORT_DATA.csv')


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
df['Date'] = pd.to_datetime(df['Date'])

# Defining a function to extract month and week numbers
def extract_month_week(item):
    month, week = re.match(r'([A-Za-z]+) Week (\d+)', item).groups()
    month_order = {
        'Jan': 0,
        'Feb': 1,
        'Mar': 2,
        'Apr': 3,
        'May': 4,
        'Jun': 5,
        'Jul': 6,
        'Aug': 7,
        'Sep': 8,
        'Oct': 9,
        'Nov': 10,
        'Dec': 11
    }
    return month_order[month], int(week)


def get_week_name(date):
    # month = date.strftime('%B')
    week_number = ((date.day - 1) // 7) + 1
    return week_number

df['week'] = df['Date'].dt.strftime('%U').astype(int)
df['year'] = df['Date'].dt.year
df['week_of_month'] = df['Date'].apply(get_week_name)
df['week_of_year'] = df['Date'].dt.strftime('%U').astype(int)
df['month'] = df['Date'].dt.strftime('%b')
df['month_numric'] = df['Date'].apply(lambda x: x.month)


df = df[(df['Status'] == status_type) & (df['Count'] == count_type) & (df['Student Type'] == student_type) & (df['Term Type'] == term_type)]

df_grouped = df.groupby(['Aid Year', 'month_numric','month', 'week_of_year', 'week_of_month'], as_index=False)[plot_option].mean()
# df_grouped = df.groupby(['Aid Year', 'month', 'week_of_year', 'week_of_month'], as_index=False)[plot_option].mean()

df_grouped['month_week_format'] = df_grouped['month'].astype(str) + ' ' + df_grouped['week_of_year'].astype(str)
df_grouped['required_format_week_month'] = df_grouped['month'].astype(str) + ' Week ' + df_grouped['week_of_month'].astype(str)
df_grouped = df_grouped.sort_values(['month_numric', 'month_week_format'])
# df_grouped[:5]
# df_grouped = df_grouped.sort_values('week')

fig1 = px.scatter(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
             labels={plot_option: plot_option, 'week_of_year': 'Week', 'year': 'Year'},
             width=1400, height=400, color_discrete_sequence=px.colors.qualitative.G10)
fig1.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

# fig2 = px.line(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
#              labels={plot_option: plot_option, 'week_of_year': 'Week', 'year': 'Year'},
#              width=1400, height=400, color_discrete_sequence=px.colors.qualitative.G10)
# fig2.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

new_year = 2024
df['Date'] = df['Date'].apply(lambda x: x.replace(year=new_year))
df = df.sort_values('Date')
df['Date(month_day)'] = df['Date'].apply(lambda x: x.strftime('%b') + '-' +str(x.day))

fig2 = px.scatter(df, x='Date', y=plot_option, color='Aid Year',
             hover_data={'Date': False, plot_option: True, 'Date(month_day)':True})

fig2.update_traces(mode='lines+markers')

# fig2 = px.line(df_grouped, x='week_of_year', y=plot_option, color='Aid Year',
#              labels={plot_option: plot_option, 'week': 'Week', 'year': 'Year', 'month': 'month'},
#              title='Weekly Total Admit Count Over Years')
# fig.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

# fig2.update_xaxes(ticktext=df_grouped['required_format_week_month'].unique(),
#                   tickvals=df_grouped['week_of_year'].unique(), tickangle=90)
# fig2.update_layout(xaxis_title='Month/Week')
# fig.show()

######################### new graph ###########################
sorted_required_format_week_month = sorted(df_grouped['required_format_week_month'].unique(), key=extract_month_week)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Dec']
df_grouped['Temp_count'] = 0

current_count = 1
for month in months:
    week_of_months_list = sorted(df_grouped[df_grouped['month'] == month]['week_of_month'].unique())
    for week in week_of_months_list:
        df_grouped.loc[(df_grouped['month'] == month) & (df_grouped['week_of_month'] == week), 'Temp_count'] = current_count
        current_count += 1
print('Done')        

df_grouped = df_grouped.sort_values('week_of_year')
fig_3 = px.scatter(df_grouped, x='Temp_count', y=plot_option, color='Aid Year', color_discrete_sequence=px.colors.qualitative.G10)
#              labels={'Total Admit Count': 'Total Admit Count', 'week': 'Week', 'year': 'Year', 'month': 'month'})
# fig.update_xaxes(title_text="Week", tickvals=np.arange(54), ticktext=['Week {}'.format(i) for i in range(54)])

fig_3.update_traces(mode='lines+markers')
fig_3.update_xaxes(ticktext=sorted_required_format_week_month,
                  tickvals=sorted(df_grouped['Temp_count'].unique()), tickangle=90)
# fig.update_layout(xaxis_title='Month/Week')
# fig.show()
#########################


st.subheader('Weekly {t} Over Years'.format(t=plot_option))
st.plotly_chart(fig1, use_container_width=True)


st.subheader('Weekly {t} Over Years'.format(t=plot_option))
st.plotly_chart(fig2, use_container_width=True)


st.subheader('Weekly {t} Over Years'.format(t=plot_option))
st.plotly_chart(fig_3, use_container_width=True)
