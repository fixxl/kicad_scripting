import pcbnew

class Elecrow_Design_Rules( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Enforce Elecrow design rules"
        self.category = "Modify PCB"
        self.description = "Set design rules according to Elecrow.com. Run DRC afterwards!"

    def Run( self ):
        pcb = pcbnew.GetBoard()

        design_settings = pcb.GetDesignSettings()

        # Set absolute minimum values
        design_settings.m_ViasMinAnnulus = 150000
        design_settings.m_TrackMinWidth = 150000
        design_settings.m_ViasMinSize = 600000
        design_settings.m_CopperEdgeClearance = 500000
        design_settings.m_SolderMaskMinWidth = 0
        design_settings.m_SolderMaskMargin = 0
        
        ViaMinDrill = design_settings.m_ViasMinSize - 2*design_settings.m_ViasMinAnnulus

        #xx = design_settings.GetDefault()
        #xx.SetClearance(200000)
        #xx.SetTrackWidth(200000)
        #xx.SetViaDrill(300000)
        #xx.SetViaDiameter(800000)
        
        for m in pcb.GetTracks():          
            if (m.GetClass()=="TRACK"):
                if(m.GetWidth() < design_settings.m_TrackMinWidth):
                    m.SetWidth(design_settings.m_TrackMinWidth)
            elif (m.GetClass()=="VIA"):
                if(m.GetWidth() < design_settings.m_ViasMinSize):
                    m.SetWidth(design_settings.m_ViasMinSize)
                if(m.Cast().GetDrill() < ViaMinDrill):
                    m.Cast().SetDrill(ViaMinDrill)

if __name__ == "__main__":
    Elecrow_Design_Rules().Run()