'''
    A python script example to create various plot files from a board:
    Fab files
    Doc files
    Gerber files

    Important note:
        this python script does not plot frame references.
        the reason is it is not yet possible from a python script because plotting
        plot frame references needs loading the corresponding page layout file
        (.wks file) or the default template.

        This info (the page layout template) is not stored in the board, and therefore
        not available.

        Do not try to change SetPlotFrameRef(False) to SetPlotFrameRef(true)
        the result is the pcbnew lib will crash if you try to plot
        the unknown frame references template.
'''

import pcbnew
import os
from Print_Board_Dimensions import *

class Create_Output( pcbnew.ActionPlugin ):
    def defaults (self):
        self.name = "Create fabrication output and documentation"
        self.category = "PCB data generation"
        self.description = "Create fabrication output and documentation"


    def Run (self):      
        Print_Board_Dimensions().Run()
        
        board = pcbnew.GetBoard()

        ff = board.GetFileName().replace("\\","/")
        while("//" in r"%r" % ff):
            ff = ff.replace("//", "/")
        
        fdir = ff.rsplit("/", 1)[0:-1][0] + "/"
        fname = (ff.rsplit(".", 1)[0]).rsplit("/", 1)[-1]

        fabdir = fdir + "fabrication/"
        dokudir = fdir + "documentation/"
        mapfiledir = dokudir + "drillmaps/"

        if not (os.path.isdir(fabdir)):
            os.mkdir(fabdir)
        if not (os.path.isdir(dokudir)):
            os.mkdir(dokudir)
        if not (os.path.isdir(mapfiledir)):
            os.mkdir(mapfiledir)

        pctl = pcbnew.PLOT_CONTROLLER(board)
        popt = pctl.GetPlotOptions()

        # Set some important plot options:
        popt.SetPlotFrameRef(False)
        popt.SetSketchPadLineWidth(pcbnew.FromMM(0.05))

        popt.SetAutoScale(False)
        popt.SetScale(1)
        popt.SetMirror(False)
        popt.SetUseGerberAttributes(True)
        popt.SetGerberPrecision(6)
        popt.SetExcludeEdgeLayer(True)
        popt.SetSubtractMaskFromSilk(True)
        popt.SetUseAuxOrigin(True)
        popt.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)

        popt.SetOutputDirectory(fabdir)

        # Once the defaults are set it become pretty easy...
        # I have a Turing-complete programming language here: I'll use it...
        # param 0 is a string added to the file base name to identify the drawing
        # param 1 is the layer ID
        # param 2 is a comment
        rename_necessary = False

        plot_plan = [
            ( "TopLayer", pcbnew.F_Cu, "Top layer" ),
            ( "BottomLayer", pcbnew.B_Cu, "Bottom layer" ),
            ( "PasteBottom", pcbnew.B_Paste, "Paste Bottom" ),
            ( "PasteTop", pcbnew.F_Paste, "Paste top" ),
            ( "SilkTop", pcbnew.F_SilkS, "Silk top" ),
            ( "SilkBottom", pcbnew.B_SilkS, "Silk top" ),
            ( "MaskBottom", pcbnew.B_Mask, "Mask bottom" ),
            ( "MaskTop", pcbnew.F_Mask, "Mask top" ),
            ( "Mechanical", pcbnew.Edge_Cuts, "Mechanical" ),
        ]

        popt.SetUseGerberProtelExtensions(True)
        
        for layer_info in plot_plan:
            if layer_info[1] <= pcbnew.B_Cu:
                popt.SetSkipPlotNPTH_Pads( True )
            else:
                popt.SetSkipPlotNPTH_Pads( False )
            pctl.SetLayer(layer_info[1])
            pctl.OpenPlotfile("", pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
            filpn = pctl.GetPlotFileName().rsplit('.',1)[0:-1][0]
            extn = pctl.GetPlotFileName().rsplit('.', 1)[-1]
            pctl.PlotLayer()
            
            if extn == 'gm1':
                rename_necessary = True
                sysstrng = (filpn + ".gm1")
                newname = (filpn + ".gml")

        #generate internal copper layers, if any
        lyrcnt = board.GetCopperLayerCount();

        for innerlyr in range ( 1, lyrcnt-1 ):
            pctl.SetLayer(innerlyr)
            lyrname = 'inner%s' % innerlyr
            pctl.OpenPlotfile(lyrname, pcbnew.PLOT_FORMAT_GERBER, "inner")
            pctl.PlotLayer()


        # At the end you have to close the last plot, otherwise you don't know when
        # the object will be recycled!
        pctl.ClosePlot()

        if rename_necessary:
            if os.path.isfile(newname):
                os.remove(newname)
            os.rename(sysstrng, newname)
            rename_necessary = False

        # Fabricators need drill files.
        # sometimes a drill map file is asked (for verification purpose)
        drlwriter = pcbnew.EXCELLON_WRITER( board )
        drlwriter.SetMapFileFormat( pcbnew.PLOT_FORMAT_PDF )

        mirror = False
        minimalHeader = False
        offset = board.GetAuxOrigin()
        # False to generate 2 separate drill files (one for plated holes, one for non plated holes)
        # True to generate only one drill file
        mergeNPTH = False
        drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )

        metricFmt = True
        drlwriter.SetFormat( metricFmt, pcbnew.GENDRILL_WRITER_BASE.SUPPRESS_LEADING, 3, 3 )

        drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), True, False );
        drlwriter.CreateDrillandMapFilesSet( mapfiledir , False, True );

        # Rename drill files to .txt
        if os.path.isfile(fabdir + fname + "-PTH.drl"):
            if os.path.isfile(fabdir + fname + "-PTH.txt"):
                os.remove(fabdir + fname + "-PTH.txt")
            os.rename(fabdir + fname + "-PTH.drl", fabdir + fname + "-PTH.txt")
        if os.path.isfile(fabdir + fname + "-NPTH.drl"):
            if os.path.isfile(fabdir + fname + "-NPTH.txt"):
                os.remove(fabdir + fname + "-NPTH.txt")
            os.rename(fabdir + fname + "-NPTH.drl", fabdir + fname + "-NPTH.txt")
        
        os.system("zip -j " + fabdir + fname + ".zip " + fabdir + "*")

        #######################################################################################################

        popt.SetA4Output(True)
        popt.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
        # popt.SetAutoScale(True)
        
        # Switching the output directory
        popt.SetOutputDirectory(dokudir)

        ########################################################################################################

        # Our fabricators want two additional gerbers:
        # An assembly with no silk trim and all and only the references
        # (you'll see that even holes have designators, obviously)
        # popt.SetSubtractMaskFromSilk(False)
        popt.SetPlotReference(True)
        popt.SetPlotValue(False)
        popt.SetPlotInvisibleText(False)
        popt.SetPlotReference(True)
        popt.SetPlotValue(True)
        popt.SetPlotInvisibleText(False)

        # Remember that the frame is always in color 0 (BLACK) and should be requested
        # before opening the plot
        popt.SetPlotFrameRef(False)
        
        popt.SetFineScaleAdjustX(1.000)
        popt.SetFineScaleAdjustY(1.000)       
        
        pctl.OpenPlotfile("Layout", pcbnew.PLOT_FORMAT_PDF, "General layout")
        popt.SetTextMode(pcbnew.PLOTTEXTMODE_STROKE)

        pctl.SetLayer(pcbnew.Edge_Cuts)
        pctl.PlotLayer()

        popt.SetPlotMode(pcbnew.NO_FILL)     
        pctl.SetLayer(pcbnew.F_Mask)
        pctl.PlotLayer()

        popt.SetPlotMode(pcbnew.FILLED_SHAPE)
        pctl.SetLayer(pcbnew.F_SilkS)
        pctl.PlotLayer()
        
        pctl.ClosePlot()
        
        ################################################################################################################
        
        pctl.OpenPlotfile("Assembly", pcbnew.PLOT_FORMAT_SVG, "Master Assembly")
        pctl.SetColorMode(True)

        # We want *everything*
        popt.SetPlotReference(True)
        popt.SetPlotValue(True)
        popt.SetPlotInvisibleText(False)

        # Remember than the DXF driver assigns colours to layers. This means that
        # we will be able to turn references on and off simply using their layers
        # Also most of the layer are now plotted in 'line' mode, because DXF handles
        # fill mode almost like sketch mode (this is to keep compatibility with
        # most CAD programs; most of the advanced primitive attributes required are
        # handled only by recent autocads...); also the entry level cads (qcad
        # and derivatives) simply don't handle polyline widths...

        pctl.SetLayer(pcbnew.B_SilkS)
        pctl.PlotLayer()
        pctl.SetLayer(pcbnew.F_SilkS)
        pctl.PlotLayer()
        popt.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.SMALL_DRILL_SHAPE)
        pctl.SetLayer(pcbnew.B_Mask)
        pctl.PlotLayer()
        pctl.SetLayer(pcbnew.F_Mask)
        pctl.PlotLayer()
        pctl.SetLayer(pcbnew.B_Paste)
        pctl.PlotLayer()
        pctl.SetLayer(pcbnew.F_Paste)
        pctl.PlotLayer()
        pctl.SetLayer(pcbnew.Edge_Cuts)
        pctl.PlotLayer()

        # Export the copper layers too... exporting one of them in filled mode with
        # drill marks will put the marks in the WHITE later (since it tries to blank
        # the pads...); these will be obviously great reference points for snap
        # and stuff in the cad. A pctl function to only plot them would be
        # better anyway...

        
        #pctl.SetLayer(pcbnew.B_Cu)
        #pctl.PlotLayer()
        #popt.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)
        #pctl.SetLayer(pcbnew.F_Cu)
        #pctl.PlotLayer()

        # At the end you have to close the last plot, otherwise you don't know when
        # the object will be recycled!
        pctl.ClosePlot()
        
        
if __name__ == "__main__":
    Create_Output().Run()