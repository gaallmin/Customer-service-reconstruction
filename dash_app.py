# dash_app.py
import dash
from dash import dcc, html
import plotly.express as px
from models import SessionLocal, UserFeedback
from collections import Counter

def create_dash_app(server):
    # Create a Dash app that uses the existing Flask server
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash/'
    )

    # Layout of the dash app
    dash_app.layout = html.Div(children=[
        html.H1(children='Ankh App Data Analysis'),

        dcc.Dropdown(
            id='text-source-dropdown',
            options=[
                {'label': 'Reservation Opinion', 'value': 'reservation_opinion'},
                {'label': 'Health Issues', 'value': 'health_issues'},
                {'label': 'Ankh Help', 'value': 'ankh_help'},
            ],
            value='reservation_opinion'
        ),

        dcc.Graph(id='word-frequency-graph'),
    ])

    # Callback to update the graph based on the selected text column
    @dash_app.callback(
        dash.dependencies.Output('word-frequency-graph', 'figure'),
        [dash.dependencies.Input('text-source-dropdown', 'value')]
    )
    def update_graph(selected_column):
        # Query from DB
        db = SessionLocal()
        feedbacks = db.query(UserFeedback).all()
        db.close()

        # Concatenate all text in the selected column
        texts = [getattr(f, selected_column) for f in feedbacks if getattr(f, selected_column)]
        combined_text = " ".join(texts)

        # Simple tokenization (for demonstration). 
        # For Korean text, consider morphological analysis (e.g., KoNLPy).
        tokens = combined_text.split()

        # Count frequencies
        counter = Counter(tokens)
        most_common = counter.most_common(20)  # top 20 words

        # Convert to a DataFrame or list for Plotly
        words = [item[0] for item in most_common]
        counts = [item[1] for item in most_common]

        fig = px.bar(x=words, y=counts, labels={'x': 'Word', 'y': 'Count'}, title='Top Word Frequencies')
        return fig

    return dash_app

# If you want to run the Dash app standalone, do something like this:
if __name__ == '__main__':
    from flask import Flask
    server = Flask(__name__)

    dash_app = create_dash_app(server)
    server.run(debug=True, port=8050)
