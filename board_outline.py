import pcbnew

class board_outline( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Set board outline"
        self.category = "Modify PCB"
        self.description = "Small outline to guarantee small tolerance at manufacturing"

    def Run( self ):
        pcb = pcbnew.GetBoard()

        # Board outline
        frame = pcb.GetDrawings()
        for f in frame:
            if (f.GetLayerName()=="Edge.Cuts"):
                f.SetWidth(pcbnew.FromMM(0.01))