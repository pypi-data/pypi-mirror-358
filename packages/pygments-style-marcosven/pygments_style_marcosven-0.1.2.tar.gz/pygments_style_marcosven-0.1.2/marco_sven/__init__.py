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
        Token:              "#D5BE99",
        Comment:            "italic #5D544B",
        Keyword:            "bold #7DAEA3",
        Name.Function:      "#A9B665",
        Name.Class:         "#DAA758",
        Name.Variable:      "#B8BB26",
        Name.Builtin:       "#83A598",
        String:             "#89B482",
        Number:             "#EA6962",
        Operator:           "#E78A4E",
        Generic.Heading:    "bold #D3869B",
        Generic.Subheading: "bold #D3869B",
    }
