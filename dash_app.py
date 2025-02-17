# dash_app.py
import dash
from dash import dcc, html
import plotly.express as px
from models import SessionLocal, UserFeedback
from collections import Counter
from util.analysis_utils import predict_sentiments

try:
    from konlpy.tag import Okt
    okt = Okt()
    HAVE_KONLPY = True
except ImportError:
    HAVE_KONLPY = False

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
        dcc.Graph(id='sentiment-graph')
    ])

    # Callback to update the graph based on the selected text column
    @dash_app.callback(
        [dash.dependencies.Output('word-frequency-graph', 'figure'),
        dash.dependencies.Output('sentiment-graph', 'figure')],
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

        if HAVE_KONLPY:
            tokens=[]
            for txt in texts:
                tokens.extend(okt.nouns(txt))
        else:
            tokens = combined_text.split()

        stopwords = {"reservation_opinion": {"예약"},
                     "health_issues": {"있어서", "있어요","있습니다"},
                     "ankh_help": {"수"}}
        selected_stopwords = stopwords.get(selected_column, set())
        filtered_token = [token for token in tokens if token not in selected_stopwords]

        # Count frequencies
        counter = Counter(filtered_token)
        most_common = counter.most_common(20)  # top 20 words

        # Convert to a DataFrame or list for Plotly
        words = [word for word, count in most_common]
        counts = [count for word, count in most_common]

        word_freq_fig = px.bar(
            x=words, 
                     y=counts, 
                     labels={'x': 'Word', 'y': 'Count'}, 
                     title='Top Word Frequencies')

        sentiment_labels = predict_sentiments(texts)
        sentiment_counter = Counter(sentiment_labels)
        sentiment_names = list(sentiment_counter.keys())
        sentiment_values = list(sentiment_counter.values())

        sentiment_fig = px.pie(
            names=sentiment_names,
            values=sentiment_values,
            title='Sentiment Distribution (Transformer-based)'
        )
        return word_freq_fig, sentiment_fig

    return dash_app
