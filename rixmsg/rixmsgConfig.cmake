# Get the directory containing this file.
get_filename_component(RIX_MSG_CURRENT_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)

# Set the location of your headers.
set(RIX_MSG_INC "~/.rix/include/")

# Load the settings into the current CMake project.
include(${RIX_MSG_CURRENT_DIR}/rixmsgTargets.cmake)
