import pcbnew
import math

class Print_Board_Dimensions ( pcbnew.ActionPlugin ):

    def defaults( self ):
        self.name = "Print Board Dimensions"
        self.category = "Add Documentation"
        self.description = "Tries to get board dimensions and prints information to Cmts_User-Layer"
    
    
    def Run(self):
        pcb = pcbnew.GetBoard()
        
        min_x = None
        min_y = None
        max_x = None
        max_y = None

        # Small board outline
        pcbdrawings = pcb.GetDrawings()
        i = 0
        for f in pcbdrawings:
            if (f.GetLayerName()=="Edge.Cuts"):
                f.SetWidth(pcbnew.FromMM(0.01))
                if (i==0):
                    min_x = f.GetStart().x
                    min_y = f.GetStart().y
                    max_x = f.GetStart().x
                    max_y = f.GetStart().y
                
                if(f.GetShape() == 3):
                    rad = ((f.GetStart()[0] - f.GetEnd()[0])**2 + (f.GetStart()[1] - f.GetEnd()[1])**2)**0.5
                    min_x = min(f.GetStart().x - rad, min_x)
                    min_y = min(f.GetStart().y - rad, min_y)
                    max_x = max(f.GetStart().x + rad, max_x)
                    max_y = max(f.GetStart().y + rad, max_y)    

                else:
                    if(f.GetShape() == 2):
                        rad = ((f.GetStart()[0] - f.GetEnd()[0])**2 + (f.GetStart()[1] - f.GetEnd()[1])**2)**0.5
                        ang = int(f.GetAngle())
                        ang_start = int(f.GetArcAngleStart())                        
                        
                        if(ang < 0):
                            ang_range = range(ang_start, ang_start + ang - 1, -1)
                        else:
                            ang_range = range(ang_start, ang_start + ang + 1, 1)                       
                        
                        for ll in ang_range:
                            px = f.GetStart()[0] + rad * math.cos(math.radians(ll/10))
                            py = f.GetStart()[1] + rad * math.sin(math.radians(ll/10))                           
                            min_x = min(px, min_x)
                            min_y = min(py, min_y)
                            max_x = max(px, max_x)
                            max_y = max(py, max_y)
                    
                    else:
                        min_x = min(f.GetStart().x, min_x)
                        min_y = min(f.GetStart().y, min_y)
                        max_x = max(f.GetStart().x, max_x)
                        max_y = max(f.GetStart().y, max_y)
                        min_x = min(f.GetEnd().x, min_x)
                        min_y = min(f.GetEnd().y, min_y)
                        max_x = max(f.GetEnd().x, max_x)
                        max_y = max(f.GetEnd().y, max_y)
                
                i += 1     
               
        if (i > 0):
            dim_x = math.ceil(pcbnew.ToMM(max_x - min_x))
            dim_y = math.ceil(pcbnew.ToMM(max_y - min_y))
            
            addnew = True
            tt = pcbnew.TEXTE_PCB(pcb)
            
            for drawing in pcb.GetDrawings():              
                if isinstance(drawing,pcbnew.TEXTE_PCB): 
                    if (drawing.GetText().split(':', 1)[0]=="Board dimensions" and drawing.GetLayer() == pcbnew.Cmts_User and drawing.GetPosition()[0] == 178300000 and drawing.GetPosition()[1] == 174000000):
                        tt = drawing                   
                        addnew = False                          
            
            tt.SetText("Board dimensions: %dmm x %dmm" % (dim_x, dim_y))
            tt.SetHorizJustify(-1)
            tt.SetTextThickness(pcbnew.FromMM(0.2))
            tt.SetPosition(pcbnew.wxPointMM(178.3, 174))
            tt.SetLayer(pcbnew.Cmts_User)
            
            if (addnew):
                pcb.Add(tt)
                
            pcb.SetAuxOrigin(pcbnew.wxPoint(min_x, min_y))

if __name__ == "__main__":
    Print_Board_Dimensions().Run()