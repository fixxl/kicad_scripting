import pcbnew
import wx
import re
import os

class Make_BOM( pcbnew.ActionPlugin ):    
    
    def defaults( self ):
        self.name = "Make Bill of Materials (BOM)"
        self.category = "Documentation"
        self.description = "Create a textfile with all modules used in the PCB"

        
    def Run (self):
        class displayDialog(wx.Dialog):
            def __init__(self, parent):
                wx.Dialog.__init__(self, parent, id=-1, title="Choose BOM format", size = (250,100))#
                
                self.perform_changes = False
                self.format_is_latex = False

                self.panel = wx.Panel(self) 
                vbox = wx.GridSizer(2, 2, 0, 0) 
                
                l1 = wx.StaticText(self.panel, -1, "Which format: ") 
                vbox.Add(l1, 0, wx.EXPAND) 
                ApplyToList = ['Plain Text', 'PDF (needs LaTeX)']           
                self.t1 = wx.ComboBox(self.panel, choices=ApplyToList)
                self.t1.SetSelection(0)                                
                vbox.Add(self.t1,0, wx.EXPAND)
                
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
                
            def on_ok_clicked(self, event):
                self.perform_changes = True
                self.format_is_latex = (self.t1.GetValue()=='PDF (needs LaTeX)')
                self.Destroy()
                
            def on_cancel_clicked(self, event):
                self.perform_changes = False
                self.Destroy()
                


        def FillWithSpaces(occupied_slots, total_slots):
            return(" " * (max(total_slots - occupied_slots,0)))
            
        def FormStr(strng, latexbom=True):
            if latexbom:
                strng = strng.replace("_", "\_")
            
            return strng
        
        
        frame = displayDialog(None)
        frame.ShowModal() 
        
        if frame.perform_changes:
            latexbom = frame.format_is_latex
            
            pcb = pcbnew.GetBoard()
            
            fileroot = str(pcb.GetFileName().rsplit('.', 1)[0]).replace("\\", "/")
            filepath = fileroot.rsplit("/", 1)[0]
            
            if latexbom:
                filename = fileroot + "_bom.tex"
            else:
                filename = fileroot + "_bom.txt"
            
            # Initialise maximum lengths
            refmaxlen = 7
            valmaxlen = 3
            packmaxlen = 0
            
            reftype = []
            partsinpcb = []
            
            mods = pcb.GetModules()
            
            for m in mods:
                if((str(m.GetFPID().GetUniStringLibItemName()[0:12]) != "MountingHole") and (str(m.GetFPID().GetUniStringLibItemName()[0:9]) != "TestPoint")):
                    refmaxlen = max(len(m.GetReference()), refmaxlen)
                    valmaxlen = max(len(m.GetValue()), valmaxlen)
                    packmaxlen = max(len(str(m.GetFPID().GetUniStringLibItemName())), packmaxlen)
                    reftype.append(str(re.split('[0-9,\*]', m.GetReference(), 1)[0]))
                    
            reftype = sorted(list(set(reftype)))
            
            if(" ") in reftype:
                reftype.remove(" ")        
            
            refmaxlen += 4
            valmaxlen += 4
                  
            filecontent = []
            
            # LaTeX Document Header
            if latexbom:
                filecontent.append("\\documentclass[paper=a4]{scrartcl}\n\n\\usepackage[intlimits]{amsmath}\n\\usepackage{amsfonts, amssymb, array, longtable, tabu, scrlayer-scrpage, fontspec, unicode-math, icomma, textcomp, microtype}\n\\usepackage[hang]{caption}\n\\usepackage[per-mode=fraction, locale=DE,detect-all=true]{siunitx}\n\\usepackage[margin=15mm, bottom=5mm,  includefoot]{geometry}\n\\usepackage{polyglossia}\n\\usepackage[autostyle]{csquotes}\n\n\\newcommand{\\origttfamily}{}\n\\let\\origttfamily=\\ttfamily\n\\renewcommand{\\ttfamily}{\\origttfamily\n\\hyphenchar\\font=`\\-}\n\\setmainfont{TeX Gyre Termes}\n\\setsansfont{Latin Modern Sans}[Scale=MatchLowercase]\n\\setmonofont{LMMonoLt10-Bold}[Scale=MatchLowercase]\n\n\\defaultfontfeatures{Ligatures=TeX}\n\n\\begin{document}\n\\begin{center}\n\\textbf{\\large\\sffamily%")
            
            # Print pcb-name
            headline = FormStr(str("Bill of materials for " + pcb.GetFileName().replace('\\','/').rsplit('/', 1)[1]), latexbom)
            filecontent.append(headline)
            if latexbom:
                filecontent.append("}\n\\end{center}\n\n\\subsection*{Index of parts}\n\n\\begin{longtabu} to \\textwidth[l]{lX[-1]X}")
            else:
                filecontent.append("=" * len(headline))
                filecontent.append("")
                filecontent.append("Index of parts")
                    
            filecontent.append("Reference{}Value/Name{}Package{}".format(" & " if latexbom else FillWithSpaces(len("Reference"), refmaxlen), " & " if latexbom else FillWithSpaces(len("Value/Name"), valmaxlen), " \\\\ \\hline\\hline\n\\endhead" if latexbom else ""))
            
            if not latexbom:
                filecontent.append("-" * (refmaxlen - 2) + "  " + "-" * (valmaxlen - 2) + "  " + "-" * (packmaxlen))
            
            for typus in reftype:
                newgroup = 1
                for i in range(0, 500):
                    if (isinstance(pcb.FindModuleByReference(typus + str(i)), pcbnew.MODULE)):
                        if newgroup == 1:
                            newgroup = 2
                            filecontent.append(typus + " & & \\\\" if latexbom else typus)
                        m = pcb.FindModuleByReference(typus + str(i))
                        filecontent.append("{}{}{}{}{}{}".format(FormStr(m.GetReference(), latexbom), " & " if latexbom else FillWithSpaces(len(m.GetReference()), refmaxlen), FormStr(m.GetValue(), latexbom), " & " if latexbom else FillWithSpaces(len(m.GetValue()), valmaxlen), FormStr(str(m.GetFPID().GetUniStringLibItemName()), latexbom), "\\\\" if latexbom else ""))
                        
                        partsinpcb.append(str(re.split('[0-9,\*]', m.GetReference(), 1)[0] + " " + str(m.GetFPID().GetUniStringLibItemName()) + " " + m.GetValue()))
                        
                if newgroup == 2:
                    filecontent.append("\\hline\n" if latexbom else "")
            
            # Create shopping list according to Reference letter(s)
            numofparts = dict((i, partsinpcb.count(i)) for i in partsinpcb)
            
            partsinpcb = []
            valpackpairs = dict()
            valnumpairs = dict()
            
            for k in numofparts:
                d1 = {k.split(" ", 1)[1]: k.split(" ", 1)[0]}
                d2 = {k.split(" ", 1)[1]: numofparts[k]}
                
                if d1.keys()[0] not in valpackpairs.keys():
                    valpackpairs.update(d1)
                else:
                    if(ord(k.split(" ", 1)[0]) > ord(valpackpairs[d1.keys()[0]])):
                        valpackpairs[d1.keys()[0]] += "/" + k.split(" ", 1)[0]
                    else:
                        valpackpairs[d1.keys()[0]] = k.split(" ", 1)[0] + "/" + valpackpairs[d1.keys()[0]]
                    
                if d2.keys()[0] not in valnumpairs.keys():
                    valnumpairs.update(d2)
                else:
                    valnumpairs[d2.keys()[0]] += numofparts[k]
            
            
            # Update keys in the dictionary
            for k in valnumpairs.keys():
                valnumpairs[valpackpairs[k] + " " + k] = valnumpairs[k]
                del valnumpairs[k]
               
            
            oldtype = sorted(valnumpairs)[0].split(" ", 1)[0]
            for key in sorted(valnumpairs.iterkeys()):
                if(latexbom):
                    if key.split(" ", 2)[0] != oldtype:
                        partsinpcb.append("\\hline")
                    partsinpcb.append("%s & %s & %s & %s \\\\" % (FormStr(key.split(" ", 2)[0]), FormStr(key.split(" ", 2)[1]), FormStr(key.split(" ", 2)[2]), valnumpairs[key]))
                else:
                    if key.split(" ", 2)[0] != oldtype:
                        partsinpcb.append("")
                    partsinpcb.append("%s%s%s%s%s%s%s" % (key.split(" ", 2)[0], FillWithSpaces(len(key.split(" ", 2)[0]), refmaxlen), key.split(" ", 2)[1], FillWithSpaces(len(key.split(" ", 2)[1]), packmaxlen+4), key.split(" ", 2)[2], FillWithSpaces(len(key.split(" ", 2)[2]), valmaxlen), valnumpairs[key]))
                oldtype = key.split(" ", 2)[0]
            
            if latexbom:
                filecontent.append("\\end{longtabu}\n\\vspace{20mm}\n\\newpage\n\\subsection*{Shopping list}\n\n\\begin{longtabu} to \\textwidth[l]{lXX[-1]c}")
            else:
                filecontent.append("")
                filecontent.append("Shopping list")
            
            filecontent.append("Type{}Package{}Value/Name{}Quantity{}".format(" & " if latexbom else FillWithSpaces(len("Type"), refmaxlen), " & " if latexbom else FillWithSpaces(len("Package"), packmaxlen+4), " & " if latexbom else FillWithSpaces(len("Value/Name"), valmaxlen)," \\\\ \\hline\\hline\n\\endhead" if latexbom else ""))
            
            if not latexbom:
                filecontent.append("-" * (refmaxlen - 2) + "  " + "-" * (packmaxlen + 2) + "  " + "-" * (valmaxlen-2) + "  " + "-" * len("Quantity"))
            
            for p in partsinpcb:
                filecontent.append(p)
            
            if latexbom:
                filecontent.append("\\hline\n\\end{longtabu}\n\\end{document}")
            
            with open(filename, 'w') as f:
                for fc in filecontent:
                    f.write("%s\n" % fc)
                    
            if(latexbom):                
                os.chdir(filepath)
                os.system("lualatex --shell-escape -interaction=nonstopmode \"" + filename + "\"")
                
                endings = ["aux", "synctex.gz", "log", "tex"]
                for ee in endings:
                    if (os.path.isfile(fileroot + "_bom." + ee)):
                        os.remove(fileroot + "_bom." + ee)
                
            
if __name__ == "__main__":
    Make_BOM().Run()
