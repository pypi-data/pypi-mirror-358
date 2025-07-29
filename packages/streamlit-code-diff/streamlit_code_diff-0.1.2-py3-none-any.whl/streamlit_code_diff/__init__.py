"""
Streamlit Code Diff Component

A Streamlit component for code diff visualization using v-code-diff.
"""

import os
from typing import Optional, Literal, Dict, Any
import streamlit.components.v1 as components

# Create a _component_func which will call the frontend component.
# We create this here so it doesn't get recreated every time the function is called.
# And assign an `url` if you're in development mode.
_component_func = components.declare_component(
    "streamlit_code_diff",
    path=os.path.join(os.path.dirname(__file__), "frontend", "build"),
)


def st_code_diff(
    old_string: str,
    new_string: str,
    language: str = "plaintext",
    output_format: Literal["line-by-line", "side-by-side"] = "side-by-side",
    diff_style: Literal["word", "char"] = "word",
    context: int = 5,
    filename: Optional[str] = None,
    new_filename: Optional[str] = None,
    theme: Optional[Literal["light", "dark"]] = None,
    trim: bool = True,
    no_diff_line_feed: bool = True,
    height: Optional[str] = None,
    force_inline_comparison: bool = False,
    hide_header: bool = False,
    hide_stat: bool = False,
    ignore_matching_lines: Optional[str] = None,
    key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Render a code diff visualization using v-code-diff.

    Parameters
    ----------
    old_string : str
        Original code content
    new_string : str
        Modified code content
    language : str, default "plaintext"
        Programming language for syntax highlighting
    output_format : {"line-by-line", "side-by-side"}, default "side-by-side"
        Display format for the diff
    diff_style : {"word", "char"}, default "word"
        Highlight differences at word or character level
    context : int, default 5
        Number of context lines around changes
    filename : str, optional
        Original filename to display
    new_filename : str, optional
        New filename to display
    theme : {"light", "dark"}, optional
        Force light or dark theme (auto-detects if None)
    trim : bool, default True
        Remove leading/trailing whitespace
    no_diff_line_feed : bool, default True
        Ignore line ending differences
    height : str, optional
        Maximum height of component (e.g., "300px", "50vh")
    force_inline_comparison : bool, default False
        Force inline comparison (word or char level)
    hide_header : bool, default False
        Hide header bar
    hide_stat : bool, default False
        Hide statistical part in header bar
    ignore_matching_lines : str, optional
        Pattern to ignore matching lines (e.g., '(time|token)')
    key : str, optional
        Unique component key

    Returns
    -------
    dict
        Dictionary with diff statistics: {isChanged: bool, addNum: int, delNum: int}

    Examples
    --------
    >>> import streamlit as st
    >>> from streamlit_code_diff import st_code_diff
    >>>
    >>> old_code = "def hello():\n    print('Hello')"
    >>> new_code = "def hello(name='World'):\n    print(f'Hello, {name}!')"
    >>>
    >>> result = st_code_diff(
    ...     old_string=old_code,
    ...     new_string=new_code,
    ...     language="python",
    ...     filename="hello.py"
    ... )
    >>> st.write(f"Changes detected: {result['isChanged']}")
    >>>
    >>> # Advanced usage with all options
    >>> result = st_code_diff(
    ...     old_string=old_code,
    ...     new_string=new_code,
    ...     language="python",
    ...     output_format="line-by-line",
    ...     diff_style="char",
    ...     context=10,
    ...     height="400px",
    ...     force_inline_comparison=True,
    ...     hide_header=True,
    ...     ignore_matching_lines="(debug|console)"
    ... )
    """

    component_value = _component_func(
        old_string=old_string,
        new_string=new_string,
        language=language,
        output_format=output_format,
        diff_style=diff_style,
        context=context,
        filename=filename,
        new_filename=new_filename,
        theme=theme,
        trim=trim,
        no_diff_line_feed=no_diff_line_feed,
        height=height,
        force_inline_comparison=force_inline_comparison,
        hide_header=hide_header,
        hide_stat=hide_stat,
        ignore_matching_lines=ignore_matching_lines,
        key=key,
        default={"isChanged": False, "addNum": 0, "delNum": 0},
    )

    return component_value


# Make st_code_diff available at package level
__all__ = ["st_code_diff"]
