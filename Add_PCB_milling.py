#  Add_PCB_milling.py
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
import math
import pcbnew

class Add_PCB_milling( pcbnew.ActionPlugin ):

    def defaults( self ):
        self.name = "Add PCB milling"
        self.category = "Modify PCB"
        self.description = "Add milling to the PCB, milling tool radius can be considered"

    def Run( self ):
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Add milling")#
                
                self.perform_changes = False
                self.center_x = pcbnew.ToMM(pcbnew.GetBoard().GetDesignSettings().m_GridOrigin[0])
                self.center_y = pcbnew.ToMM(pcbnew.GetBoard().GetDesignSettings().m_GridOrigin[1])
                self.length_x = 0
                self.length_y = 0
                self.radius = 0
                self.corner_outside = False

                self.panel = wx.Panel(self) 
                vbox = wx.GridSizer(7, 2, 0, 0) 
                
                l1 = wx.StaticText(self.panel, -1, "Center X (leave blank for origin):") 
                vbox.Add(l1, 1, wx.ALIGN_RIGHT|wx.ALL,5)        
                self.t1 = wx.TextCtrl(self.panel)                              
                self.t1.Bind(wx.EVT_TEXT, self.OnKeyTyped1)
                vbox.Add(self.t1,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5)

                l2 = wx.StaticText(self.panel, -1, "Center Y (leave blank for origin):") 
                vbox.Add(l2, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t2 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t2,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t2.Bind(wx.EVT_TEXT,self.OnKeyTyped2)

                l3 = wx.StaticText(self.panel, -1, "Length X (mm):") 
                vbox.Add(l3, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t3 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t3,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t3.Bind(wx.EVT_TEXT,self.OnKeyTyped3)

                l4 = wx.StaticText(self.panel, -1, "Length Y (mm):") 
                vbox.Add(l4, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t4 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t4,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t4.Bind(wx.EVT_TEXT,self.OnKeyTyped4)            

                l5 = wx.StaticText(self.panel, -1, "Tool radius (mm):") 
                vbox.Add(l5, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                self.t5 = wx.TextCtrl(self.panel) 
                vbox.Add(self.t5,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
                self.t5.Bind(wx.EVT_TEXT,self.OnKeyTyped5)
                
                l6 = wx.StaticText(self.panel, -1, "Corners inside/outside:") 
                vbox.Add(l6, 1, wx.ALIGN_RIGHT|wx.ALL,5) 
                ApplyToList = ['Inside', 'Outside']           
                self.t6 = wx.ComboBox(self.panel, choices=ApplyToList)
                self.t6.SetSelection(0)                                
                vbox.Add(self.t6,0, wx.EXPAND)
                self.t6.Bind(wx.EVT_COMBOBOX, self.on_hbox6)
                
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
            def OnKeyTyped1(self, event):
                self.center_x = self.retanum(self.t1.GetValue(), pcbnew.ToMM(pcbnew.GetBoard().GetDesignSettings().m_GridOrigin[0]))
                
            def OnKeyTyped2(self, event): 
                self.center_y = self.retanum(self.t2.GetValue(), pcbnew.ToMM(pcbnew.GetBoard().GetDesignSettings().m_GridOrigin[1]))
            
            def OnKeyTyped3(self, event): 
                self.length_x = self.retanum(self.t3.GetValue())  
            
            def OnKeyTyped4(self, event): 
                self.length_y = self.retanum(self.t4.GetValue())  
            
            def OnKeyTyped5(self, event): 
                self.radius = self.retanum(self.t5.GetValue())  
               
            def on_hbox6(self, event):
                self.corner_outside = (self.t6.GetSelection > 0)

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

        radius = pcbnew.FromMM(frame.radius)
        if(radius < 0):
            radius = 0
            
        center_x = pcbnew.FromMM(frame.center_x)
        center_y = pcbnew.FromMM(frame.center_y)

        length_x = pcbnew.FromMM(frame.length_x)
        length_y = pcbnew.FromMM(frame.length_y)

        width = pcbnew.FromMM(0.01)
        
        if frame.perform_changes and (radius <= length_x/2) and (radius <= length_y/2):
            if (radius == length_x/2) and (length_x == length_y):
                circ = pcbnew.PCB_SHAPE()
                circ.SetLayer(pcbnew.Edge_Cuts)
                circ.SetShape(pcbnew.S_CIRCLE)
                circ.SetArcStart(pcbnew.wxPoint(center_x + radius, center_y))
                circ.SetCenter(pcbnew.wxPoint(center_x, center_y))
                circ.SetWidth(width)
                pcb.Add(circ)
            
            else:
                offset = (1 - math.sqrt(2)) if frame.corner_outside else 0
                
                # Draw straight segments
                if(length_x > 2*radius):
                    south = pcbnew.PCB_SHAPE()
                    south.SetLayer( pcbnew.Edge_Cuts )
                    south.SetStart( pcbnew.wxPoint((center_x - length_x/2 + radius - offset * radius), (center_y + length_y/2)) )
                    south.SetEnd( pcbnew.wxPoint(center_x + length_x/2 - radius +  offset * radius, center_y + length_y/2)  )
                    south.SetWidth(width)
                    pcb.Add( south )

                    north = pcbnew.PCB_SHAPE()
                    north.SetLayer( pcbnew.Edge_Cuts )
                    north.SetStart( pcbnew.wxPoint((center_x - length_x/2 + radius - offset * radius), (center_y - length_y/2)) )
                    north.SetEnd( pcbnew.wxPoint(center_x + length_x/2 - radius + offset * radius, center_y - length_y/2)  )
                    north.SetWidth(width)
                    pcb.Add( north )
                
                if(length_y > 2*radius):
                    east = pcbnew.PCB_SHAPE()
                    east.SetLayer( pcbnew.Edge_Cuts )
                    east.SetStart( pcbnew.wxPoint(center_x + length_x/2, center_y - length_y/2 + radius - offset*radius) )
                    east.SetEnd( pcbnew.wxPoint(center_x + length_x/2, center_y + length_y/2 - radius + offset*radius)  )
                    east.SetWidth(width)
                    pcb.Add( east )

                    west = pcbnew.PCB_SHAPE()
                    west.SetLayer( pcbnew.Edge_Cuts )
                    west.SetStart( pcbnew.wxPoint(center_x - length_x/2, center_y - length_y/2 + radius - offset * radius) )
                    west.SetEnd( pcbnew.wxPoint(center_x - length_x/2, center_y + length_y/2 - radius + offset * radius)  )
                    west.SetWidth(width)
                    pcb.Add( west )

                # Draw quarter circles
                if (radius > 0):
                    if not frame.corner_outside:
                        southeast = pcbnew.PCB_SHAPE()
                        southeast.SetLayer( pcbnew.Edge_Cuts )
                        southeast.SetShape (pcbnew.S_ARC)
                        southeast.SetArcStart( pcbnew.wxPoint(center_x + length_x/2 - radius, center_y + length_y/2) )
                        southeast.SetCenter( pcbnew.wxPoint(center_x + length_x/2 - radius, center_y + length_y/2 - radius) )
                        southeast.SetAngle(-900)
                        southeast.SetWidth(width)
                        pcb.Add( southeast )

                        northeast = pcbnew.PCB_SHAPE()
                        northeast.SetLayer( pcbnew.Edge_Cuts )
                        northeast.SetShape (pcbnew.S_ARC)
                        northeast.SetArcStart( pcbnew.wxPoint(center_x + length_x/2, center_y - length_y/2 + radius) )
                        northeast.SetCenter( pcbnew.wxPoint(center_x + length_x/2 - radius, center_y - length_y/2 + radius) )
                        northeast.SetAngle(-900)
                        northeast.SetWidth(width)
                        pcb.Add( northeast )

                        northwest = pcbnew.PCB_SHAPE()
                        northwest.SetLayer( pcbnew.Edge_Cuts )
                        northwest.SetShape (pcbnew.S_ARC)
                        northwest.SetArcStart( pcbnew.wxPoint(center_x - length_x/2 + radius, center_y - length_y/2) )
                        northwest.SetCenter( pcbnew.wxPoint(center_x - length_x/2 + radius, center_y - length_y/2 + radius) )
                        northwest.SetAngle(-900)
                        northwest.SetWidth(width)
                        pcb.Add( northwest )

                        southwest = pcbnew.PCB_SHAPE()
                        southwest.SetLayer( pcbnew.Edge_Cuts )
                        southwest.SetShape (pcbnew.S_ARC)
                        southwest.SetArcStart( pcbnew.wxPoint(center_x - length_x/2, center_y + length_y/2 - radius) )
                        southwest.SetCenter( pcbnew.wxPoint(center_x - length_x/2 + radius, center_y + length_y/2 - radius) )
                        southwest.SetAngle(-900)
                        southwest.SetWidth(width)
                        pcb.Add( southwest )
                
                    else:
                        factor = (1 - math.sqrt(2)/2)
                    
                        southeast = pcbnew.PCB_SHAPE()
                        southeast.SetLayer( pcbnew.Edge_Cuts )
                        southeast.SetShape (pcbnew.S_ARC)
                        southeast.SetArcStart( pcbnew.wxPoint(center_x + length_x/2 - radius + offset*radius, center_y + length_y/2) )
                        southeast.SetCenter( pcbnew.wxPoint(center_x + length_x/2 - radius + factor * radius, center_y + length_y/2 - radius + factor * radius) )
                        southeast.SetAngle(-1800)
                        southeast.SetWidth(width)
                        pcb.Add( southeast )

                        northeast = pcbnew.PCB_SHAPE()
                        northeast.SetLayer( pcbnew.Edge_Cuts )
                        northeast.SetShape (pcbnew.S_ARC)
                        northeast.SetArcStart( pcbnew.wxPoint(center_x + length_x/2, center_y - length_y/2 + radius - offset * radius) )
                        northeast.SetCenter( pcbnew.wxPoint(center_x + length_x/2 - radius + factor * radius, center_y - length_y/2 + radius - factor * radius) )
                        northeast.SetAngle(-1800)
                        northeast.SetWidth(width)
                        pcb.Add( northeast )

                        northwest = pcbnew.PCB_SHAPE()
                        northwest.SetLayer( pcbnew.Edge_Cuts )
                        northwest.SetShape (pcbnew.S_ARC)
                        northwest.SetArcStart( pcbnew.wxPoint(center_x - length_x/2 + radius - offset * radius, center_y - length_y/2) )
                        northwest.SetCenter( pcbnew.wxPoint(center_x - length_x/2 + radius - factor * radius, center_y - length_y/2 + radius - factor * radius) )
                        northwest.SetAngle(-1800)
                        northwest.SetWidth(width)
                        pcb.Add( northwest )

                        southwest = pcbnew.PCB_SHAPE()
                        southwest.SetLayer( pcbnew.Edge_Cuts )
                        southwest.SetShape (pcbnew.S_ARC)
                        southwest.SetArcStart( pcbnew.wxPoint(center_x - length_x/2, center_y + length_y/2 - radius + offset * radius) )
                        southwest.SetCenter( pcbnew.wxPoint(center_x - length_x/2 + radius - factor * radius, center_y + length_y/2 - radius + factor * radius) )
                        southwest.SetAngle(-1800)
                        southwest.SetWidth(width)
                        pcb.Add( southwest )                

if __name__ == "__main__":
    Add_PCB_milling().Run()