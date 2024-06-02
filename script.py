# User Configurable Parameters 
lysisBufferVolume = 200							# This is the volume in uL of lysis buffer required to transfer between nodes.				
sampleVolume = 1								# This is the volume in uL of blood to be transferred to the lysis buffer.
lysateVolume = 5								# This is the volume in uL of lysate to be transferred into the output PCR plate. 

reactionBuffer1Volume = 20						# This is the volume in uL of reaction buffer to be transferred into the output PCR plate.
reactionBuffer2Volume = 20					# Change this to the volume in uL of additional reaction buffer required if necessary.
reactionBuffer3Volume = None					# Change this to the volume in uL of additional reaction buffer required if necessary.
reactionBuffer4Volume = None					# Change this to the volume in uL of additional reaction buffer required if necessary.

lysisPlateType = "Generic 96 Well 0.2 mL Skirted Plate"		# Replace this with any 96 Well Plate type in the Library, making sure to keep within "".
lysisPlateTypeAdapter = None								# If you are using an adapter, replace None with "Myra 96 Well Loading Block".	

lysisBufferDispenseDelay = 350								# Time in ms added after dispensing lysis buffer.

def generateOperations():
	myra.RequiresSoftwareVersion("1.4.6")

# Configure Deckware
	myra.LoadWasteTub("Myra Standard Waste Tub (Waste Socket)", "Waste")
	myra.LoadPlate("Myra 384 Well Tips", "A")
	
	mpblock = myra.LoadPlate("Myra Multipurpose Loading Block", "B")
	lysisBuffer = mpblock.AllocateLiquidNode("Lysis Buffer", "Generic 10 mL Screw Cap Bottle", colour="LightBlue")					
	
	reactionBuffer1 = mpblock.AllocateLiquidNode("Reaction Buffer 1", "Generic 2 mL Self-Standing Screw Cap Tube", colour="Pink")		
	if reactionBuffer2Volume:
		reactionBuffer2 = mpblock.AllocateLiquidNode("Reaction Buffer 2", "Generic 2 mL Self-Standing Screw Cap Tube", colour="Pink")
	if reactionBuffer3Volume:
		reactionBuffer3 = mpblock.AllocateLiquidNode("Reaction Buffer 3", "Generic 2 mL Self-Standing Screw Cap Tube", colour="Pink")
	if reactionBuffer4Volume:
		reactionBuffer4 = mpblock.AllocateLiquidNode("Reaction Buffer 4", "Generic 2 mL Self-Standing Screw Cap Tube", colour="Pink")	

	mpblock.AllocateFrom("C8", FillOrder.Horizontal)
	positiveControl = mpblock.AllocateLiquidNode("Control +", "Generic 1.5 mL Unskirted Screw Cap Tube", colour="Green")
	negativeControl = mpblock.AllocateLiquidNode("Control -", "Generic 1.5 mL Unskirted Screw Cap Tube", colour="Gray")
	
	samplePlate = myra.LoadPlate("Myra 48x Screw Cap Microcentrifuge Tube Loading Block", "C")
	sourceTubes = [samplePlate.Well[x["Source Well ID"]].AllocateLiquidNode(x["Name"] + " (Source)", tubeType = "Generic 1.5 mL Self-Standing Screw Cap Tube", colour="Red", ignoreVolumeWarnings=True) for x in samples.Valid]
	
	if lysisPlateTypeAdapter:
		lysisPlateAdapter = myra.LoadPlateAdapter(lysisPlateTypeAdapter, "D")
		lysisPlate = lysisPlateAdapter.LoadPlate(lysisPlateType)
	else: lysisPlate = myra.LoadPlate(lysisPlateType, "D")
	
	lysisNodes = [lysisPlate.AllocateLiquidNode(x["Name"] + " (Lysate)", colour="LightBlue", ignoreVolumeWarnings=True) for x in samples.Valid]
	positiveControlLysisNode = lysisPlate.AllocateLiquidNode("Positive Control Lysis Node", ignoreVolumeWarnings=True, colour="Green")
	negativeControlLysisNode = lysisPlate.AllocateLiquidNode("Negative Control Lysis Node", ignoreVolumeWarnings=True, colour="Gray")
	
	pcrPlate = myra.LoadPlate("Generic 96 Well 0.2 mL Skirted Plate", "E")
	pcrNodes = []
	reactionBuffer1Nodes = [pcrPlate.AllocateLiquidNode(x["Name"] + " (PCR Node)", colour="Pink") for x in samples.Valid if "Reaction Buffer 1" in x["Name"]]
	pcrNodes.extend(reactionBuffer1Nodes)
	if reactionBuffer2Volume:
		reactionBuffer2Nodes = [pcrPlate.AllocateLiquidNode(x["Name"] + " (PCR Node)", colour="Pink") for x in samples.Valid if "Reaction Buffer 2" in x["Name"]]
		pcrNodes.extend(reactionBuffer2Nodes)
	if reactionBuffer3Volume:
		reactionBuffer3Nodes = [pcrPlate.AllocateLiquidNode(x["Name"] + " (PCR Node)", colour="Pink") for x in samples.Valid if "Reaction Buffer 3" in x["Name"]]
		pcrNodes.extend(reactionBuffer3Nodes)
	if reactionBuffer4Volume:
		reactionBuffer4Nodes = [pcrPlate.AllocateLiquidNode(x["Name"] + " (PCR Node)", colour="Pink") for x in samples.Valid if "Reaction Buffer 4" in x["Name"]]
		pcrNodes.extend(reactionBuffer4Nodes)
	positiveControlpcrNode = pcrPlate.AllocateLiquidNode("Positive Control PCR Node", colour="Green")
	negativeControlpcrNode = pcrPlate.AllocateLiquidNode("Negative Control PCR Node", colour="Gray")
	
	
# Operations
	with OperationGroup("Transfer Lysis Buffer"):
		myra.TransferLiquid(lysisBuffer, lysisNodes, lysisBufferVolume, settings=TransferSettings.Default(pipette=PipetteParameters.Normal(dispenseDelay=lysisBufferDispenseDelay, maxTipVolume=40)), maxTipReuseCount=5)
		myra.TransferLiquid(lysisBuffer, positiveControlLysisNode, lysisBufferVolume, settings=TransferSettings.Default(pipette=PipetteParameters.Normal(dispenseDelay=lysisBufferDispenseDelay, maxTipVolume=40)), maxTipReuseCount=5)
		myra.TransferLiquid(lysisBuffer, negativeControlLysisNode, lysisBufferVolume, settings=TransferSettings.Default(pipette=PipetteParameters.Normal(dispenseDelay=lysisBufferDispenseDelay, maxTipVolume=40)), maxTipReuseCount=5)
		
	with OperationGroup("Transfer Blood and Mix"):
		myra.TransferLiquid(sourceTubes, lysisNodes, sampleVolume, settings=TransferSettings.Default(AspirateLevel.Sense(insufficientLiquid=InsufficientLiquid.AspirateFromBase), pipette=PipetteParameters.Viscous(aspirateSpeed=20, aspirateDelay=1000, dispenseSpeed=20, dispenseDelay=1000)), mixOnCompletion=MixType.Quick(mixCycles=5))
		myra.TransferLiquid(positiveControl, positiveControlLysisNode, sampleVolume, mixOnCompletion=MixType.Quick(mixCycles=5))
		myra.TransferLiquid(negativeControl, negativeControlLysisNode, sampleVolume, mixOnCompletion=MixType.Quick(mixCycles=5))
		
	with OperationGroup("Transfer Reaction Buffer"):
		with OperationGroup("Transfer Reaction Buffer 1"):
			myra.TransferLiquid(reactionBuffer1, reactionBuffer1Nodes, reactionBuffer1Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
			myra.TransferLiquid(reactionBuffer1, positiveControlpcrNode, reactionBuffer1Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
			myra.TransferLiquid(reactionBuffer1, negativeControlpcrNode, reactionBuffer1Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8)
		
		if reactionBuffer2Volume: 
			with OperationGroup("Transfer Reaction Buffer 2"):
				myra.TransferLiquid(reactionBuffer2, reactionBuffer2Nodes, reactionBuffer2Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer2, positiveControlpcrNode, reactionBuffer2Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer2, negativeControlpcrNode, reactionBuffer2Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8)			

		if reactionBuffer3Volume: 
			with OperationGroup("Transfer Reaction Buffer 3"):
				myra.TransferLiquid(reactionBuffer3, reactionBuffer3Nodes, reactionBuffer3Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer3, positiveControlpcrNode, reactionBuffer3Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer3, negativeControlpcrNode, reactionBuffer3Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8)							

		if reactionBuffer4Volume: 
			with OperationGroup("Transfer Reaction Buffer 4"):
				myra.TransferLiquid(reactionBuffer4, reactionBuffer4Nodes, reactionBuffer4Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer4, positiveControlpcrNode, reactionBuffer4Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8, ejectTip=False)
				myra.TransferLiquid(reactionBuffer4, negativeControlpcrNode, reactionBuffer4Volume, settings=TransferSettings.Viscous(), maxTipReuseCount=8)	
		
	with OperationGroup("Transfer Lysate and Mix"):
		myra.TransferLiquid(lysisNodes, pcrNodes, lysateVolume, mixOnCompletion=MixType.Quick(mixCycles=5))
		
	with OperationGroup("Transfer Control Lysates and Mix"):
		myra.TransferLiquid(positiveControlLysisNode, positiveControlpcrNode, lysateVolume, mixOnCompletion=MixType.Quick(mixCycles=5))
		myra.TransferLiquid(negativeControlLysisNode, negativeControlpcrNode, lysateVolume, mixOnCompletion=MixType.Quick(mixCycles=5))

	
# Allows operation groups to be created with indentation for readability. e.g.
# with OperationGroup("my group"):
#     myra.DoStufF()
#
class OperationGroup:
	def __init__(self, name):
		self.name = name
			
	def __enter__(self):
		myra.StartOperationGroup(self.name)

	def __exit__(self,a,b,c):
		myra.EndOperationGroup()	