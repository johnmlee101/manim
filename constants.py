import os
import numpy as np
import colour
import argparse
import sys

SCRIPT_DIR = ""
MEDIA_DIR = ""
ANIMATIONS_DIR = ""
RASTER_IMAGE_DIR = ""
SVG_IMAGE_DIR = ""
STAGED_SCENES_DIR = ""
FILE_DIR = ""
TEX_DIR = ""
SAVE_DIR = ""
TEX_IMAGE_DIR = ""
MOBJECT_DIR = ""
IMAGE_MOBJECT_DIR = ""
LIB_DIR = ""
TEX_TEXT_TO_REPLACE = ""
TEMPLATE_TEX_FILE = ""
TEMPLATE_TEXT_FILE = ""
TEMPLATE_CODE_FILE = ""
TEMPLATE_ALIGNAT_FILE = ""


def get_configuration():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file", help="path to file holding the python code for the scene"
        )
        parser.add_argument(
            "scene_name", nargs="?",
            help="Name of the Scene class you want to see",
        )
        optional_args = [
            ("-p", "--preview"),
            ("-w", "--write_to_movie"),
            ("-s", "--show_last_frame"),
            ("-l", "--low_quality"),
            ("-m", "--medium_quality"),
            ("-g", "--save_pngs"),
            ("-f", "--show_file_in_finder"),
            ("-t", "--transparent"),
            ("-q", "--quiet"),
            ("-a", "--write_all")
        ]
        for short_arg, long_arg in optional_args:
            parser.add_argument(short_arg, long_arg, action="store_true")
        parser.add_argument("-o", "--output_name")
        parser.add_argument("-n", "--start_at_animation_number")
        parser.add_argument("-r", "--resolution")
        parser.add_argument("-c", "--color")
        parser.add_argument("-d", "--output_directory")
        args = parser.parse_args()
        if args.output_name is not None:
            output_name_root, output_name_ext = os.path.splitext(
                args.output_name)
            expected_ext = '.png' if args.show_last_frame else '.mp4'
            if output_name_ext not in ['', expected_ext]:
                print("WARNING: The output will be to (doubly-dotted) %s%s" %
                      output_name_root % expected_ext)
                output_name = args.output_name
            else:
                # If anyone wants .mp4.mp4 and is surprised to only get .mp4, or such... Well, too bad.
                output_name = output_name_root
        else:
            output_name = args.output_name
        if args.output_directory is None:
            output_dir = os.path.dirname(args.file)
        else:
            output_dir = args.output_directory

    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)
    config = {
        "file": args.file,
        "scene_name": args.scene_name or "",
        "open_video_upon_completion": args.preview,
        "show_file_in_finder": args.show_file_in_finder,
        # By default, write to file
        "write_to_movie": args.write_to_movie or not args.show_last_frame,
        "show_last_frame": args.show_last_frame,
        "save_pngs": args.save_pngs,
        # If -t is passed in (for transparent), this will be RGBA
        "saved_image_mode": "RGBA" if args.transparent else "RGB",
        "movie_file_extension": ".mov" if args.transparent else ".mp4",
        "quiet": args.quiet or args.write_all,
        "ignore_waits": args.preview,
        "write_all": args.write_all,
        "output_name": output_name,
        "output_dir": output_dir,
        "start_at_animation_number": args.start_at_animation_number,
        "end_at_animation_number": None,
    }

    # Camera configuration
    config["camera_config"] = {}
    if args.low_quality:
        config["camera_config"].update(LOW_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = LOW_QUALITY_FRAME_DURATION
    elif args.medium_quality:
        config["camera_config"].update(MEDIUM_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = MEDIUM_QUALITY_FRAME_DURATION
    else:
        config["camera_config"].update(PRODUCTION_QUALITY_CAMERA_CONFIG)
        config["frame_duration"] = PRODUCTION_QUALITY_FRAME_DURATION

    # If the resolution was passed in via -r
    if args.resolution:
        if "," in args.resolution:
            height_str, width_str = args.resolution.split(",")
            height = int(height_str)
            width = int(width_str)
        else:
            height = int(args.resolution)
            width = int(16 * height / 9)
        config["camera_config"].update({
            "pixel_height": height,
            "pixel_width": width,
        })

    if args.color:
        try:
            config["camera_config"]["background_color"] = colour.Color(args.color)
        except AttributeError as err:
            print("Please use a valid color")
            print(err)
            sys.exit(2)

    # If rendering a transparent image/move, make sure the
    # scene has a background opacity of 0
    if args.transparent:
        config["camera_config"]["background_opacity"] = 0

    # Arguments related to skipping
    stan = config["start_at_animation_number"]
    if stan is not None:
        if "," in stan:
            start, end = stan.split(",")
            config["start_at_animation_number"] = int(start)
            config["end_at_animation_number"] = int(end)
        else:
            config["start_at_animation_number"] = int(stan)

    config["skip_animations"] = any([
        config["show_last_frame"] and not config["write_to_movie"],
        config["start_at_animation_number"],
    ])
    return config


def init_directories(config):
    global SCRIPT_DIR
    global MEDIA_DIR
    global ANIMATIONS_DIR
    global RASTER_IMAGE_DIR
    global SVG_IMAGE_DIR
    global STAGED_SCENES_DIR
    global FILE_DIR
    global TEX_DIR
    global SAVE_DIR
    global TEX_IMAGE_DIR
    global MOBJECT_DIR
    global IMAGE_MOBJECT_DIR
    global LIB_DIR
    global TEX_TEXT_TO_REPLACE
    global TEMPLATE_TEX_FILE
    global TEMPLATE_TEXT_FILE
    global TEMPLATE_CODE_FILE
    global TEMPLATE_ALIGNAT_FILE

    SCRIPT_DIR = config["output_dir"]
    if os.getenv("MEDIA_DIR"):
        MEDIA_DIR = os.getenv("MEDIA_DIR")
    elif os.path.exists("media_dir.txt"):
        with open("media_dir.txt", 'rU') as media_file:
            MEDIA_DIR = media_file.readline().strip()
    else:
        MEDIA_DIR = os.path.join(SCRIPT_DIR, "media")

    with open("media_dir.txt", 'w') as media_file:
        media_file.write(MEDIA_DIR)
    #
    ANIMATIONS_DIR = os.path.join(MEDIA_DIR, "animations")
    RASTER_IMAGE_DIR = os.path.join(MEDIA_DIR, "designs", "raster_images")
    SVG_IMAGE_DIR = os.path.join(MEDIA_DIR, "designs", "svg_images")
    # TODO, staged scenes should really go into a subdirectory of a given scenes directory
    STAGED_SCENES_DIR = os.path.join(ANIMATIONS_DIR, "staged_scenes")
    ###
    FILE_DIR = os.path.join(SCRIPT_DIR, "files")
    TEX_DIR = os.path.join(FILE_DIR, "Tex")
    SAVE_DIR = os.path.join(FILE_DIR, "saved_states")
    TEX_IMAGE_DIR = TEX_DIR  # TODO, What is this doing?
    # These two may be deprecated now.
    MOBJECT_DIR = os.path.join(FILE_DIR, "mobjects")
    IMAGE_MOBJECT_DIR = os.path.join(MOBJECT_DIR, "image")

    for folder in [FILE_DIR, RASTER_IMAGE_DIR, SVG_IMAGE_DIR, ANIMATIONS_DIR, TEX_DIR,
                   TEX_IMAGE_DIR, SAVE_DIR, MOBJECT_DIR, IMAGE_MOBJECT_DIR,
                   STAGED_SCENES_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    LIB_DIR = os.path.dirname(os.path.realpath(__file__))
    TEX_TEXT_TO_REPLACE = "YourTextHere"
    TEMPLATE_TEX_FILE = os.path.join(LIB_DIR, "template.tex")
    TEMPLATE_TEXT_FILE = os.path.join(LIB_DIR, "text_template.tex")
    TEMPLATE_CODE_FILE = os.path.join(LIB_DIR, "code_template.tex")
    TEMPLATE_ALIGNAT_FILE = os.path.join(LIB_DIR, "alignat_template.tex")


HELP_MESSAGE = """
   Usage:
   python extract_scene.py <module> [<scene name>]
   -p preview in low quality
   -s show and save picture of last frame
   -w write result to file [this is default if nothing else is stated]
   -o <file_name> write to a different file_name
   -l use low quality
   -m use medium quality
   -a run and save every scene in the script, or all args for the given scene
   -q don't print progress
   -f when writing to a movie file, export the frames in png sequence
   -t use transperency when exporting images
   -n specify the number of the animation to start from
   -r specify a resolution
   -c specify a background color
"""
SCENE_NOT_FOUND_MESSAGE = """
   That scene is not in the script
"""
CHOOSE_NUMBER_MESSAGE = """
Choose number corresponding to desired scene/arguments.
(Use comma separated list for multiple entries, or start-end or a range)
Choice(s): """
INVALID_NUMBER_MESSAGE = "Fine then, if you don't want to give a valid number I'll just quit"

NO_SCENE_MESSAGE = """
   There are no scenes inside that module
"""


LOW_QUALITY_FRAME_DURATION = 1. / 15
MEDIUM_QUALITY_FRAME_DURATION = 1. / 30
PRODUCTION_QUALITY_FRAME_DURATION = 1. / 60

# There might be other configuration than pixel shape later...
PRODUCTION_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 1440,
    "pixel_width": 2560,
}

HIGH_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 1080,
    "pixel_width": 1920,
}

MEDIUM_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 720,
    "pixel_width": 1280,
}

LOW_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 480,
    "pixel_width": 854,
}

DEFAULT_PIXEL_HEIGHT = PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_height"]
DEFAULT_PIXEL_WIDTH = PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_width"]

DEFAULT_POINT_DENSITY_2D = 25
DEFAULT_POINT_DENSITY_1D = 250

DEFAULT_STROKE_WIDTH = 4

FRAME_HEIGHT = 8.0
FRAME_WIDTH = FRAME_HEIGHT * DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT
FRAME_Y_RADIUS = FRAME_HEIGHT / 2
FRAME_X_RADIUS = FRAME_WIDTH / 2

SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1

DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = MED_SMALL_BUFF


# All in seconds
DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_POINTWISE_FUNCTION_RUN_TIME = 3.0
DEFAULT_WAIT_TIME = 1.0


ORIGIN = np.array((0., 0., 0.))
UP = np.array((0., 1., 0.))
DOWN = np.array((0., -1., 0.))
RIGHT = np.array((1., 0., 0.))
LEFT = np.array((-1., 0., 0.))
IN = np.array((0., 0., -1.))
OUT = np.array((0., 0., 1.))
X_AXIS = np.array((1., 0., 0.))
Y_AXIS = np.array((0., 1., 0.))
Z_AXIS = np.array((0., 0., 1.))

# Useful abbreviations for diagonals
UL = UP + LEFT
UR = UP + RIGHT
DL = DOWN + LEFT
DR = DOWN + RIGHT

TOP = FRAME_Y_RADIUS * UP
BOTTOM = FRAME_Y_RADIUS * DOWN
LEFT_SIDE = FRAME_X_RADIUS * LEFT
RIGHT_SIDE = FRAME_X_RADIUS * RIGHT

PI = np.pi
TAU = 2 * PI
DEGREES = TAU / 360

ANIMATIONS_DIR = os.path.join(MEDIA_DIR, "animations")
RASTER_IMAGE_DIR = os.path.join(MEDIA_DIR, "designs", "raster_images")
SVG_IMAGE_DIR = os.path.join(MEDIA_DIR, "designs", "svg_images")
# TODO, staged scenes should really go into a subdirectory of a given scenes directory
STAGED_SCENES_DIR = os.path.join(ANIMATIONS_DIR, "staged_scenes")
###
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_DIR = os.path.join(THIS_DIR, "files")
TEX_DIR = os.path.join(FILE_DIR, "Tex")
TEX_IMAGE_DIR = TEX_DIR  # TODO, What is this doing?
# These two may be depricated now.
MOBJECT_DIR = os.path.join(FILE_DIR, "mobjects")
IMAGE_MOBJECT_DIR = os.path.join(MOBJECT_DIR, "image")

for folder in [FILE_DIR, RASTER_IMAGE_DIR, SVG_IMAGE_DIR, ANIMATIONS_DIR, TEX_DIR,
               TEX_IMAGE_DIR, MOBJECT_DIR, IMAGE_MOBJECT_DIR,
               STAGED_SCENES_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

TEX_USE_CTEX = False
TEX_FIX_SVG = False
TEX_TEXT_TO_REPLACE = "YourTextHere"
TEMPLATE_TEX_FILE = os.path.join(THIS_DIR, "tex_template.tex" if not TEX_USE_CTEX
    else "ctex_template.tex")
with open(TEMPLATE_TEX_FILE, "r") as infile:
    TEMPLATE_TEXT_FILE_BODY = infile.read()
    TEMPLATE_TEX_FILE_BODY = TEMPLATE_TEXT_FILE_BODY.replace(
        TEX_TEXT_TO_REPLACE,
        "\\begin{align*}" + TEX_TEXT_TO_REPLACE + "\\end{align*}",
    )

FFMPEG_BIN = "ffmpeg"


# Colors

COLOR_MAP = {
    "DARK_BLUE": "#236B8E",
    "DARK_BROWN": "#8B4513",
    "LIGHT_BROWN": "#CD853F",
    "BLUE_A" : "#1C758A",
    "BLUE_B" : "#29ABCA",
    "BLUE_C" : "#58C4DD",
    "BLUE_D" : "#9CDCEB",
    "BLUE_E" : "#C7E9F1",
    "TEAL_E": "#49A88F",
    "TEAL_D": "#55C1A7",
    "TEAL_C": "#5CD0B3",
    "TEAL_B": "#76DDC0",
    "TEAL_A": "#ACEAD7",
    "GREEN_E": "#699C52",
    "GREEN_D": "#77B05D",
    "GREEN_C": "#83C167",
    "GREEN_B": "#A6CF8C",
    "GREEN_A": "#C9E2AE",
    "YELLOW_E": "#E8C11C",
    "YELLOW_D": "#F4D345",
    "YELLOW_C": "#FFFF00",
    "YELLOW_B": "#FFEA94",
    "YELLOW_A": "#FFF1B6",
    "GOLD_E": "#C78D46",
    "GOLD_D": "#E1A158",
    "GOLD_C": "#F0AC5F",
    "GOLD_B": "#F9B775",
    "GOLD_A": "#F7C797",
    "RED_E": "#CF5044",
    "RED_D": "#E65A4C",
    "RED_C": "#FC6255",
    "RED_B": "#FF8080",
    "RED_A": "#F7A1A3",
    "MAROON_E": "#94424F",
    "MAROON_D": "#A24D61",
    "MAROON_C": "#C55F73",
    "MAROON_B": "#EC92AB",
    "MAROON_A": "#ECABC1",
    "PURPLE_A" : "#644172",
    "PURPLE_B" : "#715582",
    "PURPLE_C" : "#9A72AC",
    "PURPLE_D" : "#B189C6",
    "PURPLE_E" : "#CAA3E8",
    "WHITE": "#FFFFFF",
    "BLACK": "#000000",
    "LIGHT_GRAY": "#BBBBBB",
    "LIGHT_GREY": "#BBBBBB",
    "GRAY": "#888888",
    "GREY": "#888888",
    "DARK_GREY": "#444444",
    "DARK_GRAY": "#444444",
    "GREY_BROWN": "#736357",
    "PINK": "#D147BD",
    "GREEN_SCREEN": "#00FF00",
    "ORANGE": "#FF862F",

    "ORANGE": "#FF7054",    # hsl(10, 67, 60)
    "MAGENTA_E": "#993265", # hsl(330, 67, 60)
    "MAGENTA_D": "#B23A76", # hsl(330, 67, 70)
    "MAGENTA_C": "#CC4387", # hsl(330, 67, 80)
    "MAGENTA_B": "#E54B98", # hsl(330, 67, 90)
    "MAGENTA_A": "#FF54A9", # hsl(330, 67, 100)
    "VIOLET_E": "#663399",  # hsl(270, 67, 60)
    "VIOLET_D": "#773BB2",  # hsl(270, 67, 70)
    "VIOLET_C": "#8844CC",  # hsl(270, 67, 80)
    "VIOLET_B": "#994CE5",  # hsl(270, 67, 90)
    "VIOLET_A": "#AA55FF",  # hsl(270, 67, 100)
    "TEAL_E": "#326599",    # hsl(210, 67, 60)
    "TEAL_D": "#3A76B2",    # hsl(210, 67, 70)
    "TEAL_C": "#4387CC",    # hsl(210, 67, 80)
    "TEAL_B": "#4B98E5",    # hsl(210, 67, 90)
    "TEAL_A": "#54A9FF",    # hsl(210, 67, 100)
}

for color_name,color_hex in COLOR_MAP.items():
    if color_name == "WHITE" or color_name == "BLACK":
        continue
    c = colour.Color(color_hex)
    c.set_luminance(c.get_luminance() - 0.08)
    COLOR_MAP[color_name] = c.hex

PALETTE = list(COLOR_MAP.values())
locals().update(COLOR_MAP)
for name in [s for s in list(COLOR_MAP.keys()) if s.endswith("_C")]:
    locals()[name.replace("_C", "")] = locals()[name]
