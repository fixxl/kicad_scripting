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
        design_settings.m_ViasMinDrill = 300000
        design_settings.m_TrackMinWidth = 150000
        design_settings.m_ViasMinSize = 600000

        xx = design_settings.GetDefault()
        xx.SetClearance(200000)
        xx.SetTrackWidth(200000)
        xx.SetViaDrill(300000)
        xx.SetViaDiameter(700000)
        
        for m in pcb.GetTracks():
            if (isinstance(m, pcbnew.VIA)):
                if(m.GetDrill() < design_settings.m_ViasMinDrill):
                    m.SetDrill(design_settings.m_ViasMinDrill)
                if(m.GetWidth() - m.GetDrill() < 2*design_settings.m_TrackMinWidth):
                    m.SetWidth(m.GetDrill() + 2*design_settings.m_TrackMinWidth)
            
            if (isinstance(m, pcbnew.TRACK)):
                if(m.GetWidth() < design_settings.m_TrackMinWidth):
                    m.SetWidth(design_settings.m_TrackMinWidth)

if __name__ == "__main__":
    Elecrow_Design_Rules().Run()