import pcbnew
import wx

class Set_Value_Layer ( pcbnew.ActionPlugin ):

    def defaults( self ):
        self.name = "Set Reference + Value Layer"
        self.category = "Modify PCB"
        self.description = "Allows control for references and/or values to be placed on silkscreen or not"

    def Run(self):
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Polygon settings", size = (250,150))#
                
                self.panel = wx.Panel(self) 
                vbox = wx.GridSizer(5, 2, 0, 0) 
                
                self.apply_to_all = False
                self.lay = "Fab"
                self.descriptor = 1
                self.perform_changes = False
                
                l1 = wx.StaticText(self.panel, -1, "Which objects: ") 
                vbox.Add(l1, 0, wx.EXPAND) 
                ApplyToList = ['Only selected', 'All']           
                self.t1 = wx.ComboBox(self.panel, choices=ApplyToList)
                self.t1.SetSelection(0)                                
                vbox.Add(self.t1,0, wx.EXPAND)
                self.t1.Bind(wx.EVT_COMBOBOX, self.on_hbox1)

                l2 = wx.StaticText(self.panel, -1, "Which descriptor: ") 
                vbox.Add(l2, 0, wx.EXPAND)                
                DescriptorList = ['Value', 'Reference', 'Both']
                self.t2 = wx.ComboBox(self.panel, choices=DescriptorList)
                self.t2.SetSelection(0)
                vbox.Add(self.t2,0, wx.EXPAND) 
                self.t2.Bind(wx.EVT_COMBOBOX, self.on_hbox2)

                l3 = wx.StaticText(self.panel, -1, "Place on layer: ") 
                vbox.Add(l3, 0, wx.EXPAND) 
                LayerList = ['Fab', 'Silkscreen']
                self.t3 = wx.ComboBox(self.panel, choices=LayerList)
                self.t3.SetSelection(0)
                vbox.Add(self.t3,0, wx.EXPAND)
                self.t3.Bind(wx.EVT_COMBOBOX, self.on_hbox3)

                self.t6 = wx.CheckBox(self.panel, label="Include values of test points")
                self.t6.SetValue(False)
                vbox.Add(self.t6, 0, wx.ALIGN_LEFT, 0)
                l5 = wx.StaticText(self.panel, label="") 
                vbox.Add(l5, 0, wx.ALIGN_RIGHT,0)                 

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
            def on_hbox1(self, event):
                self.apply_to_all = (self.t1.GetValue()=='All')
                
            def on_hbox2(self, event):
                self.descriptor = (self.t2.GetSelection()+1)
                
            def on_hbox3(self, event): 
                if (self.t3.GetValue()=="Silkscreen"):
                    self.lay = "SilkS"
                else:
                    self.lay = "Fab"
                    
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
        # frame.Destroy()
        
        if frame.perform_changes:       
            # Small board outline
            vals = pcb.GetModules()
            
            for m in vals:
                if m.IsSelected() or frame.apply_to_all:
                    if (frame.descriptor & 1):
                        curLayer = m.Value().GetLayerName()
                        Layerside = curLayer.split(".")[0] 

                        if (Layerside == "F") or (Layerside == "B"):
                            newLayer = "pcbnew." + Layerside + "_" + frame.lay                       
                            if (not m.Reference().GetText()[0:2]=="TP") or frame.t6.GetValue():
                                m.Value().SetLayer(eval(newLayer))           
                    
                    if (frame.descriptor & 2):
                        curLayer = m.Reference().GetLayerName()
                        Layerside = curLayer.split(".")[0] 

                        if (Layerside == "F") or (Layerside == "B"):
                            newLayer = "pcbnew." + Layerside + "_" + frame.lay                       
                            m.Reference().SetLayer(eval(newLayer))

if __name__ == "__main__":
    Set_Value_Layer().Run()