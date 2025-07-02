"""
Navigation callbacks for page switching and button styling
"""
from dash import Input, Output
import dash

def register_navigation_callbacks(app, get_page_1_layout, get_page_2_layout, get_page_3_layout, get_page_4_layout):
    """Register navigation-related callbacks"""
    
    @app.callback(
        Output('current-page', 'data'),
        [Input('page-1-btn', 'n_clicks'),
         Input('page-2-btn', 'n_clicks'),
         Input('page-3-btn', 'n_clicks'),
         Input('page-4-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_page(btn1, btn2, btn3, btn4):
        """Update current page based on button clicks"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return 1
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'page-1-btn':
            return 1
        elif button_id == 'page-2-btn':
            return 2
        elif button_id == 'page-3-btn':
            return 3
        elif button_id == 'page-4-btn':
            return 4
        return 1

    @app.callback(
        Output('page-content', 'children'),
        [Input('current-page', 'data')]
    )
    def display_page(page):
        """Display appropriate page content"""
        if page == 1:
            return get_page_1_layout()
        elif page == 2:
            return get_page_2_layout()
        elif page == 3:
            return get_page_3_layout()
        elif page == 4:
            return get_page_4_layout()
        return get_page_1_layout()

    @app.callback(
        [Output('page-1-btn', 'style'),
         Output('page-2-btn', 'style'),
         Output('page-3-btn', 'style'),
         Output('page-4-btn', 'style')],
        [Input('current-page', 'data')]
    )
    def update_nav_styles(current_page):
        """Update navigation button styles based on current page"""
        active_style = {
            'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
            'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'
        }
        inactive_style = {
            'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none', 
            'padding': '10px 20px', 'margin': '5px', 'borderRadius': '5px', 'cursor': 'pointer'
        }
        
        styles = [inactive_style, inactive_style, inactive_style, inactive_style]
        styles[current_page - 1] = active_style
        
        return styles
