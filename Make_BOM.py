import pcbnew
import re

class Make_BOM( pcbnew.ActionPlugin ):    
    
    def defaults( self ):
        self.name = "Add PCB milling"
        self.category = "Modify PCB"
        self.description = "Add milling to the PCB, milling tool radius can be considered"

        
    def Run (self):
        def FillWithSpaces(occupied_slots, total_slots):
            return(" " * (total_slots - occupied_slots))
        
        
        pcb = pcbnew.GetBoard()
        
        fileroot = pcb.GetFileName().rsplit('.', 1)[0]
        filename = fileroot + "_bom.txt"
        print(filename)
        
        # Initialise maximum lengths to 0
        refmaxlen = 7
        valmaxlen = 3
        packmaxlen = 0
        
        reftype = []
        
        mods = pcb.GetModules()
        
        for m in mods:
            if(m.GetValue()[0:12] != "MountingHole"):
                refmaxlen = max(len(m.GetReference()), refmaxlen)
                valmaxlen = max(len(m.GetValue()), valmaxlen)
                packmaxlen = max(len(str(m.GetFPID().GetUniStringLibItemName())), packmaxlen)
                reftype.append(str(re.split('[0-9,\*]', m.GetReference(), 1)[0]))
                
        reftype = sorted(list(set(reftype)))
        refmaxlen += 4
        valmaxlen += 4
        
        filecontent = []
        headline = str("Bill of materials for " + pcb.GetFileName().replace('\\','/').rsplit('/', 1)[1])
        filecontent.append(headline)
        filecontent.append("=" * len(headline))
        filecontent.append("")
        filecontent.append("Reference{}Value/Name{}Package".format(FillWithSpaces(len("Reference"), refmaxlen), FillWithSpaces(len("Value/Name"), valmaxlen)))
        filecontent.append("-" * (refmaxlen - 2) + "  " + "-" * (valmaxlen - 2) + "  " + "-" * (packmaxlen))
        
        for typus in reftype:
            filecontent.append(typus)
            for i in range(0, 500):
                if (isinstance(pcb.FindModuleByReference(typus + str(i)), pcbnew.MODULE)):
                    m = pcb.FindModuleByReference(typus + str(i))
                    filecontent.append("{}{}{}{}{}".format(m.GetReference(), FillWithSpaces(len(m.GetReference()), refmaxlen), m.GetValue(), FillWithSpaces(len(m.GetValue()), valmaxlen), str(m.GetFPID().GetUniStringLibItemName())))
            filecontent.append("")
        
        # print(filecontent)
        
        with open(filename, 'w') as f:
            for fc in filecontent:
                f.write("%s\n" % fc)
            
if __name__ == "__main__":
    Make_BOM().Run()