import pcbnew

class Elecrow_Design_Rules( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Apply Elecrow design rules"
        self.category = "Modify PCB"
        self.description = "Set design rules according to Elecrow.com"

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

if __name__ == "__main__":
    Elecrow_Design_Rules().Run()