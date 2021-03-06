import pcbnew

class Use_STEP_3D( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Use STEP-3D-models"
        self.category = "Modify PCB"
        self.description = "Change all 3D-models to STEP-files"

    def Run( self ):
        pcbfile = str(pcbnew.GetBoard().GetFileName())
        
        pcbnew.SaveBoard(pcbfile, pcbnew.GetBoard())

        with open(pcbfile,'r') as f:
            data = f.read()
        
        data = data.replace('.wrl', '.step')
        
        with open(pcbfile,'w') as f:
            f.write(data)
            
        pcb = pcbnew.LoadBoard(pcbfile)

if __name__ == "__main__":
    Use_STEP_3D().Run()