'''
execfile("anylocation\NitroPoly.py")

Example: execfile("E:\script\NitroPoly.py")

'''
import re
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
from functools import partial
import math as math


################
# get Functions
################
def getSandT(type):
    try:
        "s for shape and t for Transform"
        outVal = ""
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)
        selection_iter = om.MItSelectionList(selection)
        obj = om.MObject()
        
        while not selection_iter.isDone():
            selection_iter.getDependNode(obj)
            dagPath = om.MDagPath.getAPathTo(obj)
            dagName = str(dagPath.fullPathName())
            if len(dagName.split("|")) >2:
                if type=="s":
                    outVal = dagName.split("|")[-1]
                elif type=="t":
                    outVal = dagName.split("|")[-2]
            else:
                outVal = dagName.split("|")[-1]
            selection_iter.next()
    except:
        pass
    return outVal

def getEdgelist(shpname):
    if shpname =="" : return
    elist = []
    selection = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection)
    selection_iter = om.MItSelectionList(selection)
    selection_DagPath = om.MDagPath()
    component_edge = om.MObject()
    
    while not selection_iter.isDone():
        selection_iter.getDagPath(selection_DagPath, component_edge)
        edge_iter = om.MItMeshEdge(selection_DagPath, component_edge)
        while not edge_iter.isDone():
            #u'Teapot001.e[72667]
            elist.append(shpname +".e["+str(edge_iter.index())+"]")
            edge_iter.next()
        selection_iter.next()
    return elist

def getFacelist(shpname):
    if shpname =="" : return
    flist = []
    selection = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection)
    selection_iter = om.MItSelectionList(selection)
    selection_DagPath = om.MDagPath()
    component_face = om.MObject()

    while not selection_iter.isDone():
        selection_iter.getDagPath(selection_DagPath, component_face)
        face_iter = om.MItMeshPolygon(selection_DagPath, component_face)
        while not face_iter.isDone():
            #u'Teapot001.e[72667]
            flist.append(shpname +".f["+str(face_iter.index())+"]")
            face_iter.next()
        selection_iter.next()
    return flist

def getvertexlist(shpname):
    if shpname =="" : return
    vlist = []
    selection = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection)
    selection_iter = om.MItSelectionList(selection)
    selection_DagPath = om.MDagPath()
    component_vertex = om.MObject()

    while not selection_iter.isDone():
        selection_iter.getDagPath(selection_DagPath, component_vertex)
        vert_iter = om.MItMeshVertex(selection_DagPath, component_vertex)
        while not vert_iter.isDone():
            #u'Teapot001.e[72667]
            vlist.append(shpname +".v["+str(vert_iter.index())+"]")
            vert_iter.next()
        selection_iter.next()
    return vlist
    
def getOrderedSelection():
    '''
    Return index 0 = Edge Order
    Return index 1 = Vertex Order
    getOrderedSelection()[0][0]
    '''
    sel = cmds.ls(sl=1,fl=1) #getEdgelist(getSandT("t"))
    orSel =sel
    allVert = cmds.ls(cmds.polyListComponentConversion(sel,fe=1,tv=1),fl=1)

    vertStartandEnd = []
    for s in sel:
        cmds.select(s)
        vert = cmds.ls(cmds.polyListComponentConversion(cmds.ls(sl=1,fl=1),fe=1,tv=1),fl=1)
        V1 = vert[0]
        edgeV = cmds.ls(cmds.polyListComponentConversion(V1,fv=1,te=1),fl=1)
        inter = list(set(sel) & set(edgeV))
        if len(inter) == 1:
            vertStartandEnd.append(V1)
        V2 = vert[1]
        edgeV = cmds.ls(cmds.polyListComponentConversion(V2,fv=1,te=1),fl=1)
        inter = list(set(sel) & set(edgeV))
        if len(inter) == 1:
            vertStartandEnd.append(V2)

    vertOrder=[]
    edgeOrder=[]
    vertOrder.append(vertStartandEnd[0])
    cmds.select(vertOrder)
    for i in range(len(sel)):
        edgeV = cmds.ls(cmds.polyListComponentConversion(str(vertOrder[-1]),fv=1,te=1),fl=1)
        inter = list(set(sel) & set(edgeV))
        if len(inter) == 1:
            edgeOrder.append(str(inter[0]))
            sel = list(filter(lambda x : x != str(inter[0]), sel))
            edgeV = cmds.ls(cmds.polyListComponentConversion(inter,fe=1,tv=1),fl=1)
            bl = list(set(edgeV) - set(vertOrder))
            vertOrder.append(str(bl[0]))
    cmds.select(orSel)
    return edgeOrder,vertOrder

def getEdgeGroup():
    selEdges = cmds.ls(sl=1,fl=1)
    trans = selEdges[0].split(".")[0]
    e2vInfos = cmds.polyInfo(selEdges, ev=True)
    e2vDict = {}
    fEdges = []
    for info in e2vInfos:
        evList = [ int(i) for i in re.findall('\\d+', info) ]
        e2vDict.update(dict([(evList[0], evList[1:])]))
        
    while True:
        try:
            startEdge, startVtxs = e2vDict.popitem()
        except:
            break
        edgesGrp = [startEdge]
        num = 0
        for vtx in startVtxs:
            curVtx = vtx
            while True:
                nextEdges = []
                for k in e2vDict:
                    if curVtx in e2vDict[k]:
                        nextEdges.append(k)
                if nextEdges:
                    if len(nextEdges) == 1:
                        if num == 0:
                            edgesGrp.append(nextEdges[0])
                        else:
                            edgesGrp.insert(0, nextEdges[0])
                        nextVtxs = e2vDict[nextEdges[0]]
                        curVtx = [ vtx for vtx in nextVtxs if vtx != curVtx ][0]
                        e2vDict.pop(nextEdges[0])
                    else:
                        break
                else:
                    break
            num += 1
        fEdges.append(edgesGrp)
    retEdges =[]
    for f in fEdges:
        f= map(lambda x: (trans +".e["+ str(x) +"]"), f)
        retEdges.append(f)
        
    return retEdges

############################
# Selection modes
############################

def vertexMode():
    sel = getSandT("t")
    if sel =="":return
    mel.eval('resetPolySelectConstraint;')
    mel.eval('doMenuComponentSelection("'+ sel +'", "vertex");')
    
def edgeMode():
    sel = getSandT("t")
    if sel =="":return
    mel.eval('resetPolySelectConstraint;')
    mel.eval('doMenuComponentSelection("'+ sel+'", "edge");')

def borderMode():
    sel = getSandT("t")
    if sel =="":return
    edgeMode()
    mel.eval('polySelectConstraint -m 2 -bo 1;')
    
def faceMode():
    sel = getSandT("t")
    if sel =="":return
    mel.eval('resetPolySelectConstraint;')
    mel.eval('doMenuComponentSelection("'+ sel +'", "facet");')

def shellMode():
    sel = getSandT("t")
    if sel =="":return
    faceMode()
    pm.polySelectConstraint(shell=1)
    
############################
# Modify Selection
############################
  
def growLoop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None: return
    firstSel = getEdgelist(getSandT("t"))
    mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" 1;')
    loopEdges = getEdgelist(getSandT("t"))
    verts = pm.polyListComponentConversion(firstSel,fe=1,tv=1)
    edges = cmds.ls(pm.polyListComponentConversion(verts,fv=1,te=1),fl=1)
    edges= map(lambda x: x.encode('ascii'), edges)
    fEdges = list(set(edges) & set(loopEdges))
    pm.select(fEdges,r=1)

    
def shrinkLoop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    firstSel = getEdgelist(getSandT("t"))
    pm.select(firstSel)
    mel.eval('ConvertSelectionToVertexPerimeter;')
    edges = cmds.ls(pm.polyListComponentConversion(pm.selected(fl=1),fv=1,te=1),fl=1)
    edges= map(lambda x: x.encode('ascii'), edges)
    mel.eval('doMenuComponentSelection("'+ getSandT("t") +'", "edge");')
    pm.select(list(set(firstSel) - set(edges)))
    # Remove Borders
    for brdr in firstSel:
            vtx = cmds.ls(pm.polyListComponentConversion(brdr, fe=True, tv=True), fl=1 )
            bface = cmds.ls(pm.polyListComponentConversion(vtx, fv=True, tf=True), fl=1 )
            if len(bface) == 4:
                pm.select(brdr,d=1)
    
def growRing():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    firstSel = getEdgelist(getSandT("t"))
    mel.eval('polySelectEdgesEveryN "edgeRing" 1;')
    loopEdges = getEdgelist(getSandT("t"))
    pm.select(firstSel)
    faces = pm.polyListComponentConversion(firstSel,fe=1,tf=1)
    edges = cmds.ls(pm.polyListComponentConversion(faces,ff=1,te=1),fl=1)
    edges= map(lambda x: x.encode('ascii'), edges)
    pm.select(list(set(edges) & set(loopEdges)),r=1)

def shrinkRing():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    firstSel = getEdgelist(getSandT("t"))
    pm.select(firstSel)
    verts = cmds.ls(pm.polyListComponentConversion(pm.selected(fl=1),fe=1,tv=1),fl=1)
    pm.select(verts)
    mel.eval('ConvertSelectionToEdgePerimeter;')
    edges = getEdgelist(getSandT("t"))
    edges= map(lambda x: x.encode('ascii'), edges)
    pm.select(list(set(firstSel) - set(edges)),r=1)
    
    #Remove Border Edges
    for brdr in firstSel:
        bedge = cmds.ls(pm.polyListComponentConversion(brdr, fe=True, tf=True), fl=1 )
        if len(bedge) == 1:
            pm.select(brdr,d=1)
    
def dotLoop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    val = cmds.intField(intGap,q=1,value=1) + 1
    mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" '+ str(val) +' ;')

def dotRing():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    val = cmds.intField(intGap,q=1,value=1) + 1
    mel.eval('polySelectEdgesEveryN "edgeRing"'+ str(val) +';')

    
def hardEdge():
    sel = getSandT("t")
    if sel =="":return
    mel.eval('maintainActiveChangeSelectMode '+ sel+' ;')
    edgeMode()
    pm.select(d=1)
    mel.eval('polySelectConstraint -mode 3 -type 0x8000 -sm 1;resetPolySelectConstraint;')
    
def uvEdge():
    sel = getSandT("t")
    if sel =="":return
    mel.eval('maintainActiveChangeSelectMode '+ sel+' ;')
    #Select All Edges
    num = str(cmds.polyEvaluate(e=1))
    pm.select(sel + ".e[0:"+num+"]")
    
    #Select the borders
    temp = pm.ls(sel + ".map[*]")
    pm.select(temp)
    mel.eval('polySelectBorderShell 1;')
    mel.eval('PolySelectConvert 20;')
    pEdge = cmds.filterExpand(sm = 32, ex = 1)
    edgeDeselect = []
    for edg in pEdge:
        uvs = cmds.ls(pm.polyListComponentConversion(edg,fe=1,tuv=1),fl=1)
        if len(uvs) <=2:
            edgeDeselect.append(edg)
    pm.select(edgeDeselect,d=1)
    edgeMode()


def pointTopoint():
    if pm.filterExpand(sm=31,ex=1) is None:return
    trans = getSandT("t")
    vlist = getvertexlist(trans)
    sel = pm.selected()
    if len(sel)==2:
        sv1 = sel[0].indices()[0]
        sv2 = sel[1].indices()[0]
        edgeMode()
        pm.select(d=1)
        shortEdge = cmds.polySelect(str(trans), shortestEdgePath=(sv1,sv2))

def growFace():
    sel = getFacelist(getSandT("t"))
    cmds.ConvertSelectionToContainedEdges()
    cmds.ConvertSelectionToEdges()
    growRing()
    cmds.ConvertSelectionToFaces()

def faceBorderSel():
    chkFace = cmds.filterExpand(sm = 34, ex = True)
    if chkFace is None:return
        
    # Selection should have only two faces
    sel = getFacelist(getSandT("t"))
    if not len(sel) == 2: return
    sel= map(lambda x: x.encode('ascii'), sel)

    #Storing the object transform name
    trans = getSandT("t")
    s1faces = [sel[0]]
    s2faces = [sel[1]]
    cmds.progressWindow(title='Calculating...', progress=0,max=100, status='Processing...')
    step=1
    for i in range(0,100):
        cmds.progressWindow(e=1, progress=i, status='Calculating...')
    
        cmds.select(s1faces)
        growFace()
        s1faces = getFacelist(getSandT("t"))

        pm.select(s2faces)
        growFace()
        s2faces = getFacelist(getSandT("t"))
        
        interFaces = list(set(s1faces) & set(s2faces))
        if len(interFaces) == 2:break
    cmds.progressWindow(endProgress=1)
    # Processing to make the face border
    faceBorder = []
    for i in range(0,2):
        mel.eval('polySelectSp -loop '+sel[i] +' '+interFaces[0]  +';')
        faceBorder.append(getFacelist(getSandT("t")))
        mel.eval('polySelectSp -loop '+sel[i] +' '+interFaces[1]  +';')
        faceBorder.append(getFacelist(getSandT("t")))

    faceBorder = sum(faceBorder, [])
    faceBorder = set(cmds.ls(faceBorder,fl=1))
    faceBorder= map(lambda x: x.encode('ascii'), faceBorder)



    pm.select(d=1)
    # Getting face vertex of sel 0 and 1
    s1vertsCmds = cmds.ls(cmds.polyListComponentConversion(sel[0],ff=1,tv=1),fl=1)
    s2vertsCmds = cmds.ls(cmds.polyListComponentConversion(sel[1],ff=1,tv=1),fl=1)

    # Getting one vertex from each face
    s1verts = pm.ls(cmds.polyListComponentConversion(sel[0],ff=1,tv=1),fl=1)
    s2verts = pm.ls(cmds.polyListComponentConversion(sel[1],ff=1,tv=1),fl=1)
    sv1 = s1verts[0].indices()[0]
    sv2 = s2verts[1].indices()[0]

    # Finding shotest path between two points and removing the sel vertices
    shortEdge = cmds.polySelect(str(trans), shortestEdgePath=(sv1,sv2))
    shortVert = cmds.ls(cmds.polyListComponentConversion(getEdgelist(getSandT("t")),fe=1,tv=1),fl=1)

    combinedVerts = cmds.ls(cmds.polyListComponentConversion(faceBorder,ff=1,tv=1),fl=1)
    vertBool = list(set(shortVert) - set(combinedVerts) )
    
    # Converting the internal verts to faces
    internalFace = cmds.ls(pm.polyListComponentConversion(vertBool,fv=1,tf=1),fl=1)
    borderBool = list(set(internalFace) - set(faceBorder))
    pm.select(borderBool)
    if len(borderBool) < 1:
        pm.select(faceBorder)
        return
    
    #Looping through to get the face selection
    for i in range(0,(len(faceBorder)/4)):
        mel.eval('PolySelectTraverse 1;')
        borderInter = list(set(getFacelist(getSandT("t"))) & set(faceBorder))
        borderSubs = list(set(getFacelist(getSandT("t"))) - set(faceBorder))
        pm.select(borderSubs)
        if len(borderInter) == len(faceBorder):
            finalFaces = list(set(borderSubs) | set(faceBorder))
            pm.select(finalFaces)
            break


############################
# Object Selection
############################

def CombineClean():
    """Combine selected geometries"""
    selection = cmds.ls(sl=True, type='mesh', dag=True)
    if not selection or selection < 2: return
    # get full path
    meshFull = cmds.listRelatives(selection[0], p=True, f=True)
    # get parent
    meshParent = cmds.listRelatives(meshFull, p=True, f=True)
    meshInWorld = []
    if meshParent:
        meshParent0 = meshParent[0]
        meshInWorld.append(cmds.parent(meshFull, world=True)[0])
    else:
        meshInWorld = meshFull
    # replace 1st mesh in sel by mesh in world
    selection[0] = meshInWorld[0]
    # get pivots
    pivots = cmds.xform(meshInWorld[0], q=True, ws=True, a=True, rotatePivot=True)
    # combine & rename
    newMesh = cmds.polyUnite(selection, o=True)
    newMeshName = cmds.rename(newMesh[0], meshInWorld[0])
    # set pivot
    cmds.xform(newMeshName, rotatePivot=pivots)
    # reparent
    if meshParent:
        newMeshName = cmds.parent(newMeshName, meshParent, a=True)
  
    # delete history
    cmds.delete(newMeshName, ch=True, hi='none')
  
def detatchClean():
    faces = getFacelist(getSandT("t"))
    if faces:
        temp = faces[0].split('.')
        if not faces or len(temp) == 1 or len(faces) == cmds.polyEvaluate(f=True):return
        temp = faces[0].split('.')
        mesh = temp[0]
        temp = cmds.duplicate(mesh, n=mesh, rr=True)
        newMesh = temp[0]
        new = cmds.ls(newMesh+'.f[*]', fl=True)
        cnt = len(new)
        ii = 0
        newFaceDelete = []
        cmds.progressWindow(title='Clean Detatch - Please Wait', progress=0,max=cnt, status='Processing...', isInterruptable=True)
        for face in new:
            
            hit = False
            temp = new[ii].split('.')
            newFace = temp[1]
            o = 0
            cmds.progressWindow(e=1, progress=ii, status='Detatching...')
            for f in faces:
                
                temp = faces[o].split('.')
                oldFace = temp[1]
                o = o+1
                if newFace == oldFace:
                    hit = True
                    break
            if not hit:
                newFaceDelete.append(new[ii])
            ii = ii+1
        cmds.progressWindow(endProgress=1)
        cmds.delete(newFaceDelete)
        cmds.delete(faces)
        cmds.select(newMesh)
        cmds.xform(cp=True)
  
def UniConnector():
    ##############################
    # Selected object / components
    ##############################
    sel = pm.selected(fl=1)

    ##############
    # Object mode
    ##############
    if pm.filterExpand(sm=12) != None:
        mel.eval("dR_multiCutTool;")
        
    ##############
    # Vertex mode 
    ##############   
    elif pm.filterExpand(sm=31) != None:
        #>>>>>>>>>> Target Weld
        if len(sel) == 1:
            mel.eval('MergeVertexTool')
        elif len(sel) > 1:
            #>>>>>>>>>> Merge Verts = 0.01
            if  len(sel)==pm.polyEvaluate(v=1):
                pm.polyMergeVertex(sel,d=0.01,am=1)
            #>>>>>>>>>> Connect Tool
            else:
                pm.polyConnectComponents(sel)
            
    ###########
    #Edge mode
    ###########
    elif pm.filterExpand(sm=32) != None:
        border = pm.ls(pm.polyListComponentConversion(sel, fe=True, tf=True), fl=1 )
        
        #>>>>>>>>>> Subdivide Edge into two
        if len(sel)==1 and len(border) > 1:
            preSel = pm.polyListComponentConversion(fe = 1, tv = 1)
            pm.polySubdivideEdge(ch = 1)
            newVerts = pm.polyListComponentConversion(fe = 1, tv = 1)
            pm.select(list(set(newVerts)- set(preSel)))
            vertexMode()
       
        elif len(sel)>1:
            #border edge count
            outerBorder = []
            for e in sel:
                bCheck = pm.ls(pm.polyListComponentConversion(e, fe=True, tf=True), fl=1 )
                if len(bCheck) ==1:
                    outerBorder.append(e)

            #>>>>>>>>>> Appending polygons
            if len(sel) == 2 and len(outerBorder) == 2:
                pm.polyAppend(a=[sel[0].indices()[0],sel[1].indices()[0]])
                
            #>>>>>>>>>>  Bridging and Caping
            elif len(sel) == len(outerBorder):
                le = pm.ls(pm.polySelectSp(l=1),fl=1)
                if le == sel:
                    pm.polyCloseBorder(ch = 1)
                else:
                    pm.select(sel)
                    pm.polyBridgeEdge( ch=1, divisions = 0)
            #>>>>>>>>>>  Connecting
            else:
               pm.polyConnectComponents(sel)

    ############
    # Face mode
    ############    
               
    elif pm.filterExpand(sm=34) != None:
        sel = getFacelist(getSandT('t'))
        cmds.polyExtrudeFacet(sel)
        cmds.polyMoveFacet(ls=[1, 1, 1])
        mel.eval('performPolyMove "" 0;')
    else:
        mel.eval("dR_multiCutTool;")

  
def UniRemover():
    ##############################
    # Selected object / components
    ##############################
    sel = pm.selected(fl=1)

    ##############
    # Object mode
    ##############
    if pm.filterExpand(sm=12) != None:
        cmds.delete(sel)
        
    ##############
    # Vertex mode 
    ##############   
    elif pm.filterExpand(sm=31) != None:
        #>>>>>>>>>> Target Weld
        if len(sel) == 1:
            mel.eval('DeleteVertex;')
        elif len(sel) > 1:
            mel.eval('MergeToCenter;')
            
    ###########
    #Edge mode
    ###########
    elif pm.filterExpand(sm=32) != None:
        #>>>>>>>>>> Subdivide Edge into two
        if len(sel)==1:
            mel.eval('polyCollapseEdge;')
       
        elif len(sel)>1:
            firstSel = getEdgelist(getSandT("t"))
            mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" 1;')
            loopEdges = getEdgelist(getSandT("t"))
            pm.select(firstSel)
            fEdges = list(set(loopEdges) - set(firstSel))
            
            if fEdges:
                mel.eval('polyCollapseEdge;')
            else:
                mel.eval('DeleteEdge;')

    #-----------
    # Face mode
    #-----------
               
    elif pm.filterExpand(sm=34) != None:
        mel.eval("polyMergeToCenter;")
        faceMode()
    else:
        mel.eval("dR_multiCutTool;")

def edgeExtend():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    sel = getEdgelist(getSandT("t"))
    
    border = cmds.ls(pm.polyListComponentConversion(sel, fe=True, tf=True), fl=1 )
    if len(sel)==1 and len(border) == 1:
        #Confirming border edge
        vConvert = cmds.ls( pm.polyListComponentConversion(sel, fe=True, tv=True), fl=1)
        eConvert = cmds.ls( pm.polyListComponentConversion(vConvert, fv=True, te=True), fl=1)
        bedge = []
        for e in eConvert:
            con = cmds.ls(pm.polyListComponentConversion(e, fe=True, tf=True), fl=1 )
            if len(con) == 1:
                bedge.append(e)
        #Deselecting Original Edge and bridging
        cmds.select(list(set(bedge) - set(sel)))
        cmds.polyBridgeEdge( ch=1, divisions = 0)
        #Isolating Edges
        bridgeE = cmds.ls( pm.polyListComponentConversion(pm.selected(), fe=True, tv=True), fl=1)
        NewEdges = cmds.ls( pm.polyListComponentConversion(bridgeE, fv=True, te=True,internal=1), fl=1)
        
        pm.select(list(set(list(set(NewEdges) - set(getEdgelist(getSandT("t")))))- set(sel)))
        
def makePlanar():
    sel = cmds.ls(sl=1)
    if sel:
        fContext = cmds.currentCtx()
        cmds.setToolTo('Scale')
        cmds.manipScaleContext("Scale", e=1, mode=9)
        p = cmds.manipScaleContext("Scale", q=1, p=1)
        oa = cmds.manipScaleContext("Scale", q=1, oa=1) 
        cmds.scale(0,1,1,p=(p[0],p[1],p[2]),oa=("%srad"%oa[0],"%srad"%oa[1],"%srad"%oa[2]))
        cmds.currentCtx(fContext)

def toggleHiddenTris():
    mel.eval('TogglePolygonFaceTriangles polyOptions -r -dt 1')

def turnHiddenTris():
    if cmds.filterExpand(sm=34,ex=1) is None:return
    cmds.polyTriangulate(getFacelist(getSandT("t")))
    cmds.polyQuad(getFacelist(getSandT("t")))

def distConnect():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    sel = getEdgelist(getSandT("t"))
    if len(sel) < 2: return
    mel.eval('polySelectSp -ring '+sel[0] +' '+sel[1]  +';')
    sel = getEdgelist(getSandT("t"))
    pm.polyConnectComponents(sel)
    

def flowConnect():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    sel = getEdgelist(getSandT("t"))
    if len(sel) < 2: return
    edges = pm.polyConnectComponents(sel,insertWithEdgeFlow=1)

def spaceloop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    if len(chkEdge) <3: return
    origsel = getEdgelist(getSandT("t"))
    edgeGroup = getEdgeGroup()
    for single in edgeGroup:
        sel = single
        if len(sel) <3: return
        shp = sel[0].split(".")[0]
        #Storing both verts and edges
        verts = cmds.ls(cmds.polyListComponentConversion(sel,fe=1,tv=1),fl=1)
        edges = cmds.polyListComponentConversion(verts,fv=1,te=1, internal=1)

        # iterating for getting vertnumber and vposition
        vertData = {}
        for index, vert in enumerate(verts):
            vertData[index] = {'vertex':vert,'vertexPos':cmds.xform(vert, q=1, ws=1, t=1),'cv':None,'cvPos':None}

        #create Curve
        cmds.select(edges, r=1)
        curve = cmds.polyToCurve(form=2, degree=1)[0]

        #find the matching cv
        cvs = cmds.getAttr('{}.cv[*]'.format(curve))
        for i in range(len(cvs)):
            curveCV = '{}.cv[{}]'.format(curve,i)
            cvPos = cmds.xform(curveCV, q=1, ws=1, t=1)
            
            for vert, data in vertData.items():
                vertex = vertData[vert]['vertex']
                pos = cmds.xform(vertex, q=1, ws=1, t=1)
                roundCvPos = [round(x, 3) for x in cvPos]
                roundPos = [round(x, 3) for x in pos]
                if roundCvPos == roundPos:
                    vertData[vert]['cv'] = curveCV
                    continue

        #Building the curve
        cmds.rebuildCurve(curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=0, d=1, tol=0)

        #set New vertex postion
        for vert, data in vertData.items():
            vertex = vertData[vert]['vertex']
            curveCV = vertData[vert]['cv']
            cvPos = cmds.xform(curveCV, q=True, ws=True, t=True,a=1)
            vertData[vert]['cvPos'] = cvPos
            cmds.xform(vertex, ws=True, t=cvPos,a=1)
        cmds.delete(curve)
        
    cmds.hilite(shp)
    cmds.select(origsel, r=True)
    edgeMode()
    
def straightloop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    if len(chkEdge) <2: return
    origsel = getEdgelist(getSandT("t"))
    edgeGroup = getEdgeGroup()
    for single in edgeGroup:
        cmds.select(single)
        sel = getOrderedSelection()[1]
        B = cmds.pointPosition(sel[0])
        A = cmds.pointPosition(sel[-1])
        otherPoint = list(sel)
        otherPoint.remove(sel[0])
        otherPoint.remove(sel[-1])
        for point in otherPoint:
            C = cmds.pointPosition(point)
            Mab = math.sqrt(math.pow(B[0]-A[0],2) + math.pow(B[1]-A[1],2) + math.pow(B[2]-A[2],2))
            Mac = math.sqrt(math.pow(C[0]-A[0],2) + math.pow(C[1]-A[1],2) + math.pow(C[2]-A[2],2))
            Vab = [(B[0]-A[0])/Mab,(B[1]-A[1])/Mab,(B[2]-A[2])/Mab]
            Vac = [(C[0]-A[0])/Mac,(C[1]-A[1])/Mac,(C[2]-A[2])/Mac]
            cosA = Vab[0]*Vac[0]+Vab[1]*Vac[1]+Vab[2]*Vac[2]
            e = Mac*cosA
            E = [A[0]+Vab[0]*e,A[1]+Vab[1]*e,A[2]+Vab[2]*e]
            cmds.move(E[0],E[1],E[2],point,ws=1,wd=1)
        
    cmds.select(origsel, r=True)
    edgeMode()
    
    
def geoPoly():
    chkFace = cmds.filterExpand(sm = 34, ex = True)
    if chkFace is None:return
    
    orgSel = getFacelist(getSandT("t"))
    edges = cmds.ls(pm.polyListComponentConversion(orgSel, ff=True, te=True), fl=1 )
    brdrList =[]
    for brd in edges:
        border = cmds.ls(pm.polyListComponentConversion(brd, fe=True, tf=True), fl=1 )
        if len(border) == 1:
            brdrList.append(brd)
    cmds.ConvertSelectionToEdgePerimeter()
    tsel = cmds.ls(sl=1,fl=1)
    fset = list(tsel + brdrList)
    back2Vert = cmds.ls(pm.polyListComponentConversion(fset, fe=True, tv=True), fl=1 )
    s = back2Vert
    cmds.select(s)
    fContext = cmds.currentCtx()
    cmds.setToolTo('Move')
    s, avd, oda, cs = pm.selected(fl=1), 0, [], cmds.manipMoveContext("Move", q=1, p=1)
    cmds.select(cl=1)
    for verts in range(0, len(s), 1):
        vts = s[verts].getPosition(space='world')
        dfc = math.sqrt(pow(vts[0] - cs[0],2) + pow(vts[1] - cs[1],2) + pow(vts[2] - cs[2],2))
        oda += [(dfc)]
        avd += dfc
    avd /= len(s)
    for vert in range(0, len(s), 1):
        vts = s[vert].getPosition(space='world')
        x, y, z = (((avd / oda[vert]) * (vts[0] - cs[0])) + cs[0]), (((avd / oda[vert]) * (vts[1] - cs[1])) + cs[1]), (((avd / oda[vert]) * (vts[2] - cs[2])) + cs[2])
        s[vert].setPosition([x,y,z], space='world')
    cmds.currentCtx(fContext)
    cmds.select(fset)
    edgeMode()
    spaceloop()
    faceMode()
    cmds.select(orgSel)


def circle():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    if len(chkEdge) <4: return
    
    origsel = getEdgelist(getSandT("t"))
    edgeGroup = getEdgeGroup()
    for single in edgeGroup:
        cmds.select(single)
        fset= pm.selected(sl=1,fl=1)
        back2Vert = cmds.ls(pm.polyListComponentConversion(fset, fe=True, tv=True), fl=1 )
        pm.select(back2Vert)
        s = back2Vert
        
        fContext = cmds.currentCtx()
        cmds.setToolTo('Move')
        s, avd, oda, cs = pm.selected(fl=1), 0, [], cmds.manipMoveContext("Move", q=1, p=1)
        cmds.select(cl=1)
        for verts in range(0, len(s), 1):
            vts = s[verts].getPosition(space='world')
            dfc = math.sqrt(pow(vts[0] - cs[0],2) + pow(vts[1] - cs[1],2) + pow(vts[2] - cs[2],2))
            oda += [(dfc)]
            avd += dfc
        avd /= len(s)
        for vert in range(0, len(s), 1):
            vts = s[vert].getPosition(space='world')
            x, y, z = (((avd / oda[vert]) * (vts[0] - cs[0])) + cs[0]), (((avd / oda[vert]) * (vts[1] - cs[1])) + cs[1]), (((avd / oda[vert]) * (vts[2] - cs[2])) + cs[2])
            s[vert].setPosition([x,y,z], space='world')
        cmds.currentCtx(fContext)
        cmds.select(fset)
        spaceloop()
    edgeMode()
    cmds.select(origsel)
    
def relaxLoop():
    sel = om.MSelectionList()
    
    om.MGlobal.getActiveSelectionList(sel)
    names = []
    sel.getSelectionStrings(names)
    compSel = cmds.ls(names,fl=1)
    if compSel:
        cmds.polyAverageVertex(compSel,ch=0,i=1)
        cmds.select(compSel)

def centerloop():
    chkEdge = cmds.filterExpand(sm = 32, ex = True)
    if chkEdge is None:return
    mel.eval("polyEditEdgeFlow -adjustEdgeFlow 1;")

####################
# UI Code
####################

if cmds.window('winModelingToolkit', exists=True):
    cmds.deleteUI('winModelingToolkit')
    cmds.windowPref( 'winModelingToolkit', ra=True )
    
cmds.window('winModelingToolkit', title='NitroPoly 1.0', wh=[500, 100],mxb=0,mnb=0,rtf=1)
winWidth = 190

modelLayout = cmds.columnLayout(adjustableColumn=True)

def frameCollapseChanged(modelLayout):
    cmds.evalDeferred("cmds.window('winModelingToolkit', e=1, h=sum([eval('cmds.' + cmds.objectTypeUI(child) + '(\\'' + child + '\\', q=1, h=1)') for child in cmds.columnLayout('" + modelLayout + "', q=1, ca=1)]))")
####################
# selection
####################
cmds.frameLayout( label="Selection", cll=False)
form = cmds.formLayout(numberOfDivisions=100)
btnVert =   cmds.iconTextButton( style='iconOnly', image1='vertex_NEX.png', label='spotlight',w=30,h=30, c="vertexMode()")
btnEdge =   cmds.iconTextButton( style='iconOnly', image1='edges_NEX.png', label='spotlight',w=30,h=30 , c="edgeMode()")
btnBorder = cmds.iconTextButton( style='iconOnly', image1='traxFrameAll.png', label='spotlight',w=30,h=30 , c="borderMode()")
btnFace =   cmds.iconTextButton( style='iconOnly', image1='faces_NEX.png', label='spotlight',w=30,h=30 , c="faceMode()")
btnShell =  cmds.iconTextButton( style='iconOnly', image1='UVTkUVShell.png', label='spotlight',w=30,h=30 , c="shellMode()")
cmds.formLayout( form, edit=True, attachForm=[( btnVert, 'top', 8), ( btnVert, 'left', 10)] )
cmds.formLayout( form, edit=True, attachForm=[( btnEdge, 'top', 8), ( btnEdge, 'left', 45)] )
cmds.formLayout( form, edit=True, attachForm=[( btnBorder, 'top', 8), ( btnBorder, 'left', 80)] )
cmds.formLayout( form, edit=True, attachForm=[( btnFace, 'top', 8), ( btnFace, 'left', 115)] )
cmds.formLayout( form, edit=True, attachForm=[( btnShell, 'top', 8), ( btnShell, 'left', 150)] )

object = cmds.separator(h=1)
cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 35), ( object, 'left',0)] )
cmds.setParent('..')
cmds.setParent('..')

####################
# Modiy selection
####################
cmds.frameLayout( label="Modify Selection", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)))
cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])

cmds.button(label="Grow Loop",w=85,h=20, c="growLoop()")
cmds.button(label="Shrink Loop", w=winWidth/2-15,h=20, c="shrinkLoop()")
cmds.setParent( '..' )

cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="Grow Ring",w=85,h=20, c="growRing()")
cmds.button(label="Shrink Ring", w=winWidth/2-15,h=20, c="shrinkRing()")
cmds.setParent( '..' )

cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 1),(3, 10)])
intGap = cmds.intField(v=1, minValue=1, maxValue=100, step=1,w=30)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="Dot Loop",w=winWidth/2-30,h=20, c="dotLoop()")
cmds.button(label="Dot Ring", w=winWidth/2-30,h=20, c="dotRing()")
cmds.setParent( '..' )
cmds.setParent( '..' )

cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="Sel hard Edge", w=85,h=20, c="hardEdge()")
cmds.button(label="Sel UV Edge",w=winWidth/2-15,h=20, c="uvEdge()")
cmds.setParent( '..' )
cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="point to point", w=85,h=20, c="pointTopoint()")
cmds.button(label="Face Fill",w=winWidth/2-15,h=20, c="faceBorderSel()")
cmds.setParent( '..' )
cmds.separator(h=1,w=1)
cmds.setParent( '..' )

####################
# Object
####################
cmds.frameLayout( label="Object", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)))
cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label='Clean Combine',h=20,w=85,c="CombineClean()")
cmds.button(label='Clean Detatch',h=20,w=winWidth/2-15,c="detatchClean()" )
cmds.setParent( '..' )
cmds.separator(h=1)
cmds.setParent( '..' )
cmds.setParent( '..' )

############################
# UniConnector / UniRemover
############################
cmds.frameLayout( label="UniConnector / Remover", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)))
cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label='Connect',h=20,w=85,c="UniConnector()")
cmds.button(label='Remove',h=20,w=winWidth/2-15,c="UniRemover()")
cmds.setParent( '..' )
cmds.separator(h=1)
cmds.setParent( '..' )
cmds.setParent( '..' )

#############
# poly Tools
#############
cmds.frameLayout( label="Poly Tools", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)))
cmds.separator(h=1)

cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label='Dist Connect',h=20,w=85,c="distConnect()")
cmds.button(label='Flow Connect',h=20,w=winWidth/2-15,c="flowConnect()" )
cmds.setParent( '..' )
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label='Edge Extend',h=20,w=85,c="edgeExtend()" )
cmds.button(label='Make Planar',h=20,w=winWidth/2-15,c="makePlanar()")
cmds.setParent( '..' )
cmds.separator(h=1)
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="Space",w=85,h=20,c="spaceloop()")
cmds.button(label="Straight",w=winWidth/2-15,h=20,c="straightloop()")
cmds.setParent( '..' )
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])

cmds.button(label="Circle",w=85,h=20,c="circle()")
cmds.button(label="Geo Poly",w=winWidth/2-15,h=20,c="geoPoly()")
cmds.setParent( '..' )
cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
cmds.button(label="Relax",w=85,h=20,c="relaxLoop()")
cmds.button(label='Center',h=20,w=winWidth/2-15,c="centerloop()")
cmds.setParent( '..' )
cmds.separator(h=1)
cmds.setParent( '..' )
cmds.setParent( '..' )

cmds.showWindow()


winHeight = 0
for child in cmds.columnLayout(modelLayout, q=1, ca=1):
	winHeight += eval('cmds.' + cmds.objectTypeUI(child) + '("' + child + '", q=1, h=1)')
cmds.window( "winModelingToolkit", edit=True, widthHeight=(winWidth, winHeight),s=0)
