from pygments.style import Style
from pygments.token import Token, Comment, Keyword, Name, String, Number, Operator, Generic

class MarcoSvenStyle(Style):
    """
    A custom Pygments style for syntax highlighting.

    Attributes:
        background_color (str): The background color of the style.
        default_style (str): The default style for tokens.
    """
    background_color = "#282828"
    default_style = ""

    styles = {
        Token:              "#89B482",
        Comment:            "italic #918474",
        Keyword:            "#EA6962",
        Name.Function:      "#DAA758",
        Name.Class:         "#7DAEA3",
        Name.Variable:      "#A9B665",
        Name.Builtin:       "#D3869B",
        String:             "#DAA758",
        Number:             "#E78A4E",
        Operator:           "#E78A4E",
        Generic.Heading:    "bold #D3869B",
        Generic.Subheading: "bold #D3869B",
    }
