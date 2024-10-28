# Import required libraries
import pandas as pd
import dash
#import dash_html_components as html
#import dash_core_components as dcc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
#spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                             options=[{'label': 'All sites', 'value': 'All'}] 
                                                + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()], 
                                             value='All',
                                             placeholder='Select a Launch Site here', 
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart', 
                                                   figure=px.pie(spacex_df,
                                                                 values='class', names='Launch Site', labels={'class': 'Success'},
                                                                 title='Total Successful Launches By Site'))),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, #marks={0: '0', 100: '100'}, 
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(
                                    id='success-payload-scatter-chart', 
                                    figure=px.scatter(spacex_df, x='Payload Mass (kg)', y='class', color='Booster Version Category'))),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),  
              Input(component_id='site-dropdown', component_property='value'))

def update_pie(selected_site):
    if selected_site == 'All':
        return px.pie(spacex_df, values='class', names='Launch Site', labels={'class': 'Success'}, 
                      title='Total Successful Launches By Site')
    return px.pie((spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts().reset_index()
                   .replace({'index': {0: 'Failure', 1: 'Success'}})), 
                    values='class', names='index', labels={'class': 'Total', 'index': 'Outcome'}, 
                    #color='index', color_discrete_map={'Failure': 'red', 'Success': 'lightgreen'},
                    title='Success vs Failure for ' + selected_site)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),  
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])

def update_scatter(selected_site, selected_range):
    filtered_data = (spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_range[0]) 
                               & (spacex_df['Payload Mass (kg)'] <= selected_range[1])]
                               .replace({'class': {0: 'Failure', 1: 'Success'}}))
    
    if selected_site == 'All':
        title = title='Correlation between Payload and Success for all Sites'
    else:
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]
        title = 'Correlation between Payload and Success for ' + selected_site

    figure = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', title=title,
                        color='Booster Version Category', labels={'class': 'Outcome'})
    figure.update_traces(marker=dict(size=20, line=dict(width=1, color='white')))
    return figure


# Run the app
if __name__ == '__main__':
    app.run_server()