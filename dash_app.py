# dash_app.py
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from models import SessionLocal, UserFeedback
from collections import Counter
from util.analysis_utils import predict_sentiments

try:
    from konlpy.tag import Okt
    okt = Okt()
    HAVE_KONLPY = True
except ImportError:
    HAVE_KONLPY = False

# Global variable to store the dash app instance
_dash_app_instance = None

def create_dash_app(server):
    global _dash_app_instance
    
    # Return existing instance if already created
    if _dash_app_instance is not None:
        return _dash_app_instance
    # Create a Dash app that uses the existing Flask server
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash/',
        suppress_callback_exceptions=True
    )

    # Layout of the dash app
    dash_app.layout = html.Div(children=[
        html.H1(children='Ankh App Data Analysis', style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label('Select Feedback Category:', style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='text-source-dropdown',
                options=[
                    {'label': 'Reservation Opinion', 'value': 'reservation_opinion'},
                    {'label': 'Health Issues', 'value': 'health_issues'},
                    {'label': 'Ankh Help', 'value': 'ankh_help'},
                ],
                value='reservation_opinion',
                style={'marginBottom': '20px'}
            )
        ], style={'marginBottom': '30px'}),

        html.Div([
            html.Div([
                dcc.Graph(id='word-frequency-graph')
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(id='sentiment-graph')
            ], style={'width': '50%', 'display': 'inline-block'})
        ])
    ])

    # Callback to update the graph based on the selected text column
    @dash_app.callback(
        [dash.dependencies.Output('word-frequency-graph', 'figure'),
        dash.dependencies.Output('sentiment-graph', 'figure')],
        [dash.dependencies.Input('text-source-dropdown', 'value')]
    )
    def update_graph(selected_column):
        try:
            # Query from DB
            db = SessionLocal()
            feedbacks = db.query(UserFeedback).all()
            db.close()

            # Concatenate all text in the selected column
            texts = [getattr(f, selected_column) for f in feedbacks if getattr(f, selected_column)]
            
            # Handle empty data case
            if not texts:
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="No data available for this category",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                empty_fig.update_layout(
                    title=f"No Data Available - {selected_column.replace('_', ' ').title()}",
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, showticklabels=False)
                )
                return empty_fig, empty_fig

            combined_text = " ".join(texts)

            # Tokenization
            if HAVE_KONLPY:
                tokens = []
                for txt in texts:
                    if txt:  # Check if text is not None or empty
                        tokens.extend(okt.nouns(txt))
            else:
                tokens = combined_text.split()

            # Stopwords filtering
            stopwords = {"reservation_opinion": {"예약", "시스템", "의견"},
                         "health_issues": {"있어서", "있어요", "있습니다", "문제", "건강"},
                         "ankh_help": {"수", "도움", "앙크"}}
            selected_stopwords = stopwords.get(selected_column, set())
            filtered_tokens = [token for token in tokens if token not in selected_stopwords and len(token) > 1]

            # Count frequencies
            counter = Counter(filtered_tokens)
            most_common = counter.most_common(10)  # top 10 words for pie chart

            # Create word frequency pie chart
            if most_common:
                words = [word for word, count in most_common]
                counts = [count for word, count in most_common]
                
                word_freq_fig = px.pie(
                    values=counts,
                    names=words,
                    title=f'Top Word Distribution - {selected_column.replace("_", " ").title()}',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                word_freq_fig.update_traces(textposition='inside', textinfo='percent+label')
            else:
                # Empty pie chart
                word_freq_fig = go.Figure()
                word_freq_fig.add_annotation(
                    text="No meaningful words found after filtering",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14)
                )
                word_freq_fig.update_layout(
                    title=f'Word Distribution - {selected_column.replace("_", " ").title()}',
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, showticklabels=False)
                )

            # Sentiment analysis
            try:
                sentiment_labels = predict_sentiments(texts)
                sentiment_counter = Counter(sentiment_labels)
                sentiment_names = list(sentiment_counter.keys())
                sentiment_values = list(sentiment_counter.values())

                sentiment_fig = px.pie(
                    names=sentiment_names,
                    values=sentiment_values,
                    title='Emotion Distribution (AI Analysis)',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                sentiment_fig.update_traces(textposition='inside', textinfo='percent+label')
            except Exception as e:
                # Fallback for sentiment analysis errors
                sentiment_fig = go.Figure()
                sentiment_fig.add_annotation(
                    text=f"Sentiment analysis error: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14)
                )
                sentiment_fig.update_layout(
                    title='Emotion Distribution (AI Analysis)',
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, showticklabels=False)
                )

            return word_freq_fig, sentiment_fig

        except Exception as e:
            # Error handling
            error_fig = go.Figure()
            error_fig.add_annotation(
                text=f"Error loading data: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            error_fig.update_layout(
                title="Error",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False)
            )
            return error_fig, error_fig

    # Store the instance globally
    _dash_app_instance = dash_app
    return dash_app
