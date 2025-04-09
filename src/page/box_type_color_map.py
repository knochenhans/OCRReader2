from page.box_type import BoxType  # type: ignore

BOX_TYPE_COLOR_MAP = {
    BoxType.UNKNOWN: (0, 255, 0),  # RGB -> Teal #008080
    BoxType.FLOWING_TEXT: (255, 0, 0),  # RGB -> Red #FF0000
    BoxType.HEADING_TEXT: (255, 0, 255),  # RGB -> Maroon #800000
    BoxType.PULLOUT_TEXT: (0, 255, 255),  # RGB -> Cyan #00FFFF
    BoxType.EQUATION: (255, 255, 0),  # RGB -> Yellow #FFFF00
    BoxType.INLINE_EQUATION: (0, 0, 255),  # RGB -> Blue #0000FF
    BoxType.TABLE: (255, 128, 0),  # RGB -> Orange #FF8000
    BoxType.VERTICAL_TEXT: (128, 128, 0),  # RGB -> Olive #808000
    BoxType.CAPTION_TEXT: (128, 128, 128),  # RGB -> Gray #808080
    BoxType.FLOWING_IMAGE: (0, 0, 255),  # RGB -> Blue #0000FF
    BoxType.HEADING_IMAGE: (0, 128, 128),  # RGB -> Green #00FF00
    BoxType.PULLOUT_IMAGE: (128, 0, 0),  # RGB -> Magenta #FF00FF
    BoxType.HORZ_LINE: (64, 64, 64),  # RGB -> Dark Gray #404040
    BoxType.VERT_LINE: (64, 64, 64),  # RGB -> Dark Gray #404040
    BoxType.NOISE: (192, 192, 192),  # RGB -> Silver #C0C0C0
    BoxType.COUNT: (255, 255, 255),  # RGB -> White #FFFFFF
    BoxType.IGNORE: (0, 0, 0),  # RGB -> Black #000000
}
