### This is directly from a macro generated with ParaView; it's not great.

#### import the simple module from the paraview
import argparse

from paraview.simple import *

# Argument parsing
parser = argparse.ArgumentParser(description="ParaView Automation Script")
parser.add_argument("file_path", type=str, help="Path to the .foam file")
parser.add_argument("output_path", type=str, help="Path to save the screenshot")
args = parser.parse_args()

file_path = args.file_path
output_path = args.output_path

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Open FOAM Reader'
cl_cd_36736_3379643ce5854907980b75151ebf22b5foam = OpenFOAMReader(
    registrationName="cl_cd_36.736_3379643c-e585-4907-980b-75151ebf22b5.foam",
    FileName=file_path,
)

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

# show data in view
cl_cd_36736_3379643ce5854907980b75151ebf22b5foamDisplay = Show(
    cl_cd_36736_3379643ce5854907980b75151ebf22b5foam,
    renderView1,
    "UnstructuredGridRepresentation",
)

# trace defaults for the display properties.
cl_cd_36736_3379643ce5854907980b75151ebf22b5foamDisplay.Representation = "Surface"

# reset view to fit data
renderView1.ResetCamera(False, 0.9)

# get the material library
materialLibrary1 = GetMaterialLibrary()

# show color bar/color legend
cl_cd_36736_3379643ce5854907980b75151ebf22b5foamDisplay.SetScalarBarVisibility(
    renderView1, True
)

# update the view to ensure updated data information
renderView1.Update()

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction("p")

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction("p")

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D("p")

# ================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
# ================================================================

# get layout
layout1 = GetLayout()

# --------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(1498, 834)

# -----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.CameraPosition = [
    0.6107955647122558,
    0.05304371818758208,
    3.9651629174197653,
]
renderView1.CameraFocalPoint = [
    0.5541562754180904,
    0.20561813666944553,
    0.5923566662154927,
]
renderView1.CameraViewUp = [
    0.00031595786114208116,
    0.9989785805644513,
    0.04518512746539811,
]
renderView1.CameraParallelScale = 18.452642087245934

# create a new 'Slice'
slice1 = Slice(
    registrationName="Slice1", Input=cl_cd_36736_3379643ce5854907980b75151ebf22b5foam
)

# Properties modified on slice1.SliceType
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

# show data in view
slice1Display = Show(slice1, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
slice1Display.Representation = "Surface"

# hide data in view
Hide(cl_cd_36736_3379643ce5854907980b75151ebf22b5foam, renderView1)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction("p")

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction("p")

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D("p")

# create a new 'Stream Tracer'
streamTracer1 = StreamTracer(
    registrationName="StreamTracer1", Input=slice1, SeedType="Line"
)

# show data in view
streamTracer1Display = Show(streamTracer1, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
streamTracer1Display.Representation = "Surface"

# hide data in view
Hide(slice1, renderView1)

# show color bar/color legend
streamTracer1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# set active source
SetActiveSource(slice1)

# toggle interactive widget visibility (only when running from the GUI)
HideInteractiveWidgets(proxy=streamTracer1.SeedType)

# toggle interactive widget visibility (only when running from the GUI)
ShowInteractiveWidgets(proxy=slice1.SliceType)

# get display properties
streamTracer1Display = GetDisplayProperties(streamTracer1, view=renderView1)

# set scalar coloring
ColorBy(streamTracer1Display, ("POINTS", "U", "Magnitude"))

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction("p")

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(pLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
streamTracer1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
streamTracer1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction("U")

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction("U")

# get 2D transfer function for 'U'
uTF2D = GetTransferFunction2D("U")

# show data in view
slice1Display = Show(slice1, renderView1, "GeometryRepresentation")

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

##--------------------------------------------
## You may need to add some code at the end of this python script depending on your usage, eg:
#
## Render all views to see them appears
# RenderAllViews()
#
## Interact with the view, usefull when running from pvpython
# Interact()
#
## Save a screenshot of the active view
SaveScreenshot(output_path)
#
## Save a screenshot of a layout (multiple splitted view)
# SaveScreenshot("path/to/screenshot.png", GetLayout())
#
## Save all "Extractors" from the pipeline browser
# SaveExtracts()
#
## Save a animation of the current active view
# SaveAnimation()
#
## Please refer to the documentation of paraview.simple
## https://kitware.github.io/paraview-docs/latest/python/paraview.simple.html
##--------------------------------------------
