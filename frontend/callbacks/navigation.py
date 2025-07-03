"""
Navigation callbacks for page switching and button styling.

Usage in app.py
---------------
register_navigation_callbacks(
    app,
    ["page-1-btn", "page-2-btn", "page-3-btn", "page-4-btn"],
    [get_page_1_layout, get_page_2_layout, get_page_3_layout, get_page_4_layout],
    "page-content",
    "current-page",
)
"""

from dash import Input, Output, callback_context


def register_navigation_callbacks(
    app,
    button_ids,          # e.g. ["page-1-btn", ...]
    page_layout_funcs,   # e.g. [get_page_1_layout, ...]
    page_content_id,     # "page-content"
    store_id,            # "current-page"
):
    # ------------------------------------------------------------------ #
    # 1)  Which page are we on?  Store the answer in an invisible dcc.Store
    # ------------------------------------------------------------------ #
    @app.callback(
        Output(store_id, "data"),
        [Input(btn_id, "n_clicks") for btn_id in button_ids],
        prevent_initial_call=True,
    )
    def update_page(*_):
        ctx = callback_context
        if not ctx.triggered:
            return 1  # default to first page on first load

        clicked = ctx.triggered[0]["prop_id"].split(".")[0]
        return button_ids.index(clicked) + 1      # 1-based index

    # ------------------------------------------------------------------ #
    # 2)  Render that page’s layout in the main content <div>
    # ------------------------------------------------------------------ #
    @app.callback(
        Output(page_content_id, "children"),
        Input(store_id, "data"),
    )
    def display_page(page_num):
        idx = (page_num or 1) - 1                 # clamp just in case
        idx = max(0, min(idx, len(page_layout_funcs) - 1))
        return page_layout_funcs[idx]()

    # ------------------------------------------------------------------ #
    # 3)  Highlight the active nav button via its class name
    #     (CSS handles colours—no inline styles here!)
    # ------------------------------------------------------------------ #
    @app.callback(
        [Output(btn_id, "className") for btn_id in button_ids],
        Input(store_id, "data"),
    )
    def highlight_active(page_num):
        idx = (page_num or 1) - 1
        return [
            "nav-btn active" if i == idx else "nav-btn"
            for i in range(len(button_ids))
        ]
