# COMPASS
# ----------------------------------------------
# Configuration: http://compass-style.org/help/tutorials/configuration-reference/
#
# ----------------------------------------------
# PRODUCTION
# compass compile -e production -s compressed --no-line-comments --force --trace --time
#

# Require any additional compass plugins here.
require 'compass-notify'
require 'compass-h5bp'
require 'susy'
require 'breakpoint'

# Can be :stand_alone or :rails. Defaults to :stand_alone
project_type = :stand_alone

# paths
# Set this to the root of your project when deployed:
http_path       = "/"
css_dir         = "../css"
sass_dir        = "sass"
images_dir      = "../img"
javascripts_dir = "../js"
fonts_dir       = "../fonts"
preferred_syntax = :scss

# output option: nested, expanded, compact, compressed
output_style = :compressed

# The environment mode.
# Defaults to :production, can also be :development
# Use :development to see line numbers, file names, etc
environment = :development

# Enable/Disable line comments
line_comments = false

# Enable relative paths to assets via compass helper functions.
relative_assets = true

# disable the asset cache buster
asset_cache_buster :none

# To disable debugging comments that display the original location of your selectors. Uncomment:
# line_comments = false
#sass_options = {:debug_info => true}
