import pcbnew
import wx

class Create_Rectangular_Polygons ( pcbnew.ActionPlugin ):

    def defaults( self ):
        self.name = "Create Rectangular Polygons"
        self.category = "Modify PCB"
        self.description = "Creates Polygons for selectable net on F_Cu and B_Cu"

    def Run(self):
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Polygon settings")#
                
                self.perform_changes = False
                self.netz = 0
                self.clearance = 0.2
                self.distance = 0.5
                self.min_thickness = 0.175
                self.thermal_gap = 0.3

                self.panel = wx.Panel(self) 
                vbox = wx.GridSizer(6, 2, 0, 0) 
                
                l1 = wx.StaticText(self.panel, -1, "Connect to net:") 
                vbox.Add(l1, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                netList = [str(k) for k in pcbnew.GetBoard().GetNetsByName().keys()]           
                self.t1 = wx.ComboBox(self.panel, choices=netList)
                self.t1.SetSelection(0)                                
                self.t1.Bind(wx.EVT_COMBOBOX, self.onCombo)
                vbox.Add(self.t1,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5)

                l2 = wx.StaticText(self.panel, -1, "Clearance (mm):") 
                vbox.Add(l2, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t2 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t2,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t2.Bind(wx.EVT_TEXT,self.OnKeyTyped2)
                self.t2.SetValue("0.2")

                l3 = wx.StaticText(self.panel, -1, "Distance to board outline (mm):") 
                vbox.Add(l3, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t3 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t3,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t3.Bind(wx.EVT_TEXT,self.OnKeyTyped3)
                self.t3.SetValue("0.5")

                l4 = wx.StaticText(self.panel, -1, "Minimum thickness (mm):") 
                vbox.Add(l4, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t4 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t4,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t4.Bind(wx.EVT_TEXT,self.OnKeyTyped4)
                self.t4.SetValue("0.175")              

                l5 = wx.StaticText(self.panel, -1, "Thermal relief gap (mm):") 
                vbox.Add(l5, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t5 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t5,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t5.Bind(wx.EVT_TEXT,self.OnKeyTyped5)
                self.t5.SetValue("0.3")
                
                btn_ok = wx.Button(self.panel,-1,"OK")
                btn_ok.Bind(wx.EVT_BUTTON,self.on_ok_clicked)
                vbox.Add(btn_ok,0, wx.EXPAND)
                
                btn_cancel = wx.Button(self.panel,-1,"Cancel")
                btn_cancel.Bind(wx.EVT_BUTTON,self.on_cancel_clicked)
                vbox.Add(btn_cancel, 0, wx.EXPAND)
        
                self.panel.SetSizer(vbox)
                
                self.Centre() 
                self.Show() 
                self.Fit()  

            #----------------------------------------------------------------------
            def onCombo(self, event):
                self.netz = pcbnew.GetBoard().GetNetsByName().find(self.t1.GetValue()).value()[1].GetNet()
                
            def OnKeyTyped2(self, event): 
                self.clearance = self.retanum(event.GetString(), 0.2)
            
            def OnKeyTyped3(self, event): 
                self.distance = self.retanum(event.GetString(), 0.5)
            
            def OnKeyTyped4(self, event): 
                self.min_thickness = self.retanum(event.GetString(), 0.175)
            
            def OnKeyTyped5(self, event): 
                self.thermal_gap = self.retanum(event.GetString(), 0.3)  

            def on_ok_clicked(self, event):
                self.perform_changes = True
                self.Destroy()
                
            def on_cancel_clicked(self, event):
                self.perform_changes = False
                self.Destroy()                
            
            def retanum(self, n, alternative=0):
                try:
                    float(n)
                except ValueError:
                    return alternative
                return float(n)
        ########################################################
        #
        # Ab hier werden die Polygone erstellt
        #
        ########################################################
        
        pcb = pcbnew.GetBoard()
        
        frame = displayDialog(None)
        frame.ShowModal()
        
        netz = frame.netz
        clearance = frame.clearance
        distance = frame.distance
        min_thickness = frame.min_thickness
        thermal_gap = frame.thermal_gap
        
        
        if frame.perform_changes:       
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
                        
                    min_x = min(f.GetStart().x, min_x)
                    min_y = min(f.GetStart().y, min_y)
                    max_x = max(f.GetStart().x, max_x)
                    max_y = max(f.GetStart().y, max_y)
                    min_x = min(f.GetEnd().x, min_x)
                    min_y = min(f.GetEnd().y, min_y)
                    max_x = max(f.GetEnd().x, max_x)
                    max_y = max(f.GetEnd().y, max_y)
                    
                    i += 1

                    
            poly_min_x = (min_x + pcbnew.FromMM(distance))
            poly_max_x = (max_x - pcbnew.FromMM(distance))
            poly_min_y = (min_y + pcbnew.FromMM(distance))
            poly_max_y = (max_y - pcbnew.FromMM(distance))

            for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
                poly = pcb.InsertArea(netz, 0, layer, poly_min_x, poly_min_y, pcbnew.CPolyLine.DIAGONAL_EDGE)
                poly.SetZoneClearance(pcbnew.FromMM(clearance))
                poly.SetMinThickness(pcbnew.FromMM(min_thickness))
                poly.SetThermalReliefGap(pcbnew.FromMM(thermal_gap))
                poly.SetThermalReliefCopperBridge(pcbnew.FromMM(thermal_gap))
                poly.Outline().Append(poly_max_x, poly_min_y)
                poly.Outline().Append(poly_max_x, poly_max_y)
                poly.Outline().Append(poly_min_x, poly_max_y)
                poly.Hatch()

if __name__ == "__main__":
    Create_Rectangular_Polygons().Run()