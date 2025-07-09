open(File.openDialog("Select your cells.csv file"));

prevSlice = -1;
numCells = getValue("results.count");
sizeConv = 2/(PI*(4/3)*2.1667*2.1667*2)

Dialog.createNonBlocking("Set slice tolerance for displayed ROIs");
Dialog.addMessage("Note: A higher slice tolerance may increase loading times");
Dialog.addSlider("# of Slices +/- current slice", 0, 20, 3);
Dialog.show();
sliceTolerance = Dialog.getNumber();

while (true){
	wait(250);
	currentSlice = getSliceNumber() - 1;
	
	if (currentSlice != prevSlice) {
		
		if (prevSlice != -1){
			roiManager("deselect");
			roiManager("delete");
		}
		
		getDisplayedArea(xWindow, yWindow, wWindow, hWindow);
		
		prevSlice = currentSlice;
		n = 0;
		
		for(i = 0; i < numCells; i++){
			z = getResult("z", i);
			
			sliceDiff = abs(z-currentSlice);
			
			if (sliceDiff <= sliceTolerance){
				x = getResult("# x", i);
				
				if (x >= xWindow && x <= (xWindow + wWindow)) {
					y = getResult("y", i);
					
					if (y >= yWindow && y <= (yWindow + hWindow)) {
						size = getResult("size", i);
						intensity = getResult("source", i);
						roiSize = size*sizeConv;
						roiSize = pow(roiSize, 1/3);
						name = getResultString("name", i) + " SIZE: " + size + " VAL: " + intensity;
						makeOval(x-roiSize, y-roiSize, roiSize*2, roiSize*2);
						roiManager("add");
						roiManager("select", n);
						roiManager("rename", name);
						if (z == currentSlice) {
							roiManager("Set Color", "#00FF00");
						} else {
							roiManager("Set Color", "#FF0000");
						}
						n++;
					}
				}
			}
			else if (z > currentSlice + sliceTolerance) {
				break;
			}
			
		}
		
		roiManager("show all");
		RoiManager.useNamesAsLabels(true);
		
	}
}