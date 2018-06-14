import wx
import pcbnew

class font( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Set font sizes"
        self.category = "Modify PCB"
        self.description = "Text is put to standard format"

    def Run( self ):
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Set text parameters", size=(250, 250))#
                
                self.tw = 0.8
                self.th = 0.8
                self.thick = 0.16
                self.perform_changes = False

                self.panel = wx.Panel(self) 
                vbox = wx.GridSizer(8, 2, 0, 0) 

                l1 = wx.StaticText(self.panel, -1, "Text width (mm):") 
                vbox.Add(l1, 0, wx.ALIGN_RIGHT,0) 
                self.t1 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t1,0,wx.ALIGN_LEFT,0) 
                self.t1.Bind(wx.EVT_TEXT,self.OnKeyTyped1)
                self.t1.SetValue(str(self.tw))

                l2 = wx.StaticText(self.panel, -1, "Text height (mm):") 
                vbox.Add(l2, 0, wx.ALIGN_RIGHT,0) 
                self.t2 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t2,0,wx.ALIGN_LEFT,0) 
                self.t2.Bind(wx.EVT_TEXT,self.OnKeyTyped2)
                self.t2.SetValue(str(self.th))

                l3 = wx.StaticText(self.panel, -1, "Text thickness (mm):") 
                vbox.Add(l3, 0, wx.ALIGN_RIGHT,0) 
                self.t3 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t3,0,wx.ALIGN_LEFT,0) 
                self.t3.Bind(wx.EVT_TEXT,self.OnKeyTyped3)
                self.t3.SetValue(str(self.thick))
                
                self.t4 = wx.CheckBox(self.panel, label="Align additional reference text")
                self.t4.SetValue(True)
                vbox.Add(self.t4, 0, wx.ALIGN_LEFT, 0)
                l5 = wx.StaticText(self.panel, label="") 
                vbox.Add(l5, 0, wx.ALIGN_RIGHT,0)
                
                self.t5 = wx.CheckBox(self.panel, label="Remove text from mounting holes")
                self.t5.SetValue(True)
                vbox.Add(self.t5, 0, wx.ALIGN_LEFT, 0)
                l5 = wx.StaticText(self.panel, label="") 
                vbox.Add(l5, 0, wx.ALIGN_RIGHT,0) 
                
                self.t6 = wx.CheckBox(self.panel, label="Set values active for test points")
                self.t6.SetValue(True)
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
                   
            def OnKeyTyped1(self, event): 
                self.tw = self.retanum(event.GetString(), 0)                
            
            def OnKeyTyped2(self, event): 
                self.th = self.retanum(event.GetString(), 0)                
            
            def OnKeyTyped3(self, event): 
                self.thick = self.retanum(event.GetString(), 0)                
            
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


        pcb = pcbnew.GetBoard()
        
        frame = displayDialog(None)
        frame.ShowModal()      
        
        if (frame.perform_changes):
            # Text widths
            mods = pcb.GetModules()     
            for m in mods:
                if frame.tw > 0:
                    m.Reference().SetTextWidth(pcbnew.FromMM(frame.tw))
                if frame.th > 0:
                    m.Reference().SetTextHeight(pcbnew.FromMM(frame.th))
                if frame.thick > 0:
                    m.Reference().SetThickness(pcbnew.FromMM(frame.thick))
                
                pos = m.Reference().GetPosition()
                rot = m.Reference().GetDrawRotation()
                ang = m.Reference().GetTextAngle()
                
                for drawing in m.GraphicalItems():
                    if isinstance(drawing,pcbnew.TEXTE_MODULE) and frame.t4.GetValue(): 
                        if (drawing.GetText()=="%R"):
                            drawing.SetTextWidth(pcbnew.FromMM(frame.tw))
                            drawing.SetTextHeight(pcbnew.FromMM(frame.th))
                            drawing.SetThickness(pcbnew.FromMM(frame.thick))                         
                            drawing.SetPosition(pos)
                            drawing.Rotate(pos, rot)
                            drawing.SetTextAngle(ang)
                
                if(m.Value().GetText().split('_')[0]=="MountingHole") and frame.t5.GetValue():
                    side = "B" if m.Reference().GetLayerName()[0] == "B" else "F"
                    m.Reference().SetLayer(eval("pcbnew."+side+"_Fab"))
                    m.Reference().SetVisible(False)
                    m.SetLocked(True)
            
                if(m.Reference().GetText()[0:2]=="TP") and frame.t6.GetValue():
                    side = "B" if m.Reference().GetLayerName()[0] == "B" else "F"
                    m.Reference().SetLayer(eval("pcbnew."+side+"_Fab"))
                    m.Reference().SetVisible(False)
                    m.Value().SetLayer(eval("pcbnew."+side+"_SilkS"))
                    m.Value().SetVisible(True)

                    
                if frame.tw > 0:
                    m.Value().SetTextWidth(pcbnew.FromMM(frame.tw))
                if frame.th > 0:
                    m.Value().SetTextHeight(pcbnew.FromMM(frame.th))
                if frame.thick > 0:
                    m.Value().SetThickness(pcbnew.FromMM(frame.thick))

if __name__ == "__main__":
    font().Run()