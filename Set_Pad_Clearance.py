#  Set_Pad_Clearance.py
#
# Copyright (C) 2017 KiCad Developers, see CHANGELOG.TXT for contributors.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import wx
import pcbnew

class Set_Pad_Clearance( pcbnew.ActionPlugin ):

    def defaults( self ):
        self.name = "Set global pad clearance"
        self.category = "Modify PCB"
        self.description = "As pad clearance cannot be set globally this script loops through all the pads on the PCB"


    def Run( self ):     
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Set Pad Clearance", size=(350, 100))#

                self.panel = wx.Panel(self)
                vbox = wx.GridSizer(2, 2, 0, 0)
                
                self.perform_changes = False
                self.pclearance = 0
                
                l1 = wx.StaticText(self.panel, -1, "Global pad clearance (mm):") 
                vbox.Add(l1, 1, wx.ALIGN_RIGHT|wx.ALL,5)        
                self.t1 = wx.TextCtrl(self.panel)                              
                self.t1.Bind(wx.EVT_TEXT, self.OnKeyTyped1)
                vbox.Add(self.t1,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5)
                self.t1.SetValue("0.3")
                
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
                self.pclearance = self.retanum(self.t1.GetValue(), 0)
            
            def retanum(self, n, alternative=0):
                try:
                    float(n)
                except ValueError:
                    return alternative
                return float(n)
            
            def on_ok_clicked(self, event):
                self.pclearance = self.retanum(self.t1.GetValue(), 0)
                self.perform_changes = True
                self.Destroy()
                
            def on_cancel_clicked(self, event):
                self.perform_changes = False
                self.Destroy()    

                
        pcb = pcbnew.GetBoard()
        
        frame = displayDialog(None)
        frame.ShowModal()  

        if frame.perform_changes:
            pads=pcb.GetPads()
            for p in pads:
                p.SetLocalClearance(pcbnew.FromMM(frame.pclearance))

if __name__ == "__main__":
    Set_Pad_Clearance().Run()