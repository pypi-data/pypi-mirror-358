import disnake
from datetime import datetime

# You can customize these defaults
DEFAULT_COLOR = 0x7289DA  # A nice Discord-like blue/purple

def easy_embed(title: str, description: str, color: int = DEFAULT_COLOR) -> disnake.Embed:
    """
    Creates a standardized Disnake Embed with a title, description, and timestamp.
    
    Args:
        title (str): The title of the embed.
        description (str): The main text of the embed.
        color (int, optional): The color of the embed's side bar. Defaults to DEFAULT_COLOR.

    Returns:
        disnake.Embed: A pre-configured embed object.
    """
    embed = disnake.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Powered by CoolBot Framework")
    return embed