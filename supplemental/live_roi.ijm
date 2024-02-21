open(File.openDialog("Select your cells.csv file"));

prevSlice = -1;
numCells = getValue("results.count");
sizeConv = 1/(PI*(4/3)*3.77556*3.77556*3)

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
		
		prevSlice = currentSlice;
		n = 0;
		
		for(i = 0; i < numCells; i++){
			z = getResult("z", i);
			
			if (abs(z - currentSlice) <= sliceTolerance){
				x = getResult("# x", i);
				y = getResult("y", i);
				size = getResult("size", i);
				roiSize = size*sizeConv;
				roiSize = pow(roiSize, 1/3);
				name = getResultString("name", i) + " - " + size;
				makeOval(x-roiSize, y-roiSize, roiSize*2, roiSize*2);
				roiManager("add");
				roiManager("select", n);
				roiManager("rename", name);
				
				if (z == currentSlice){
					roiManager("Set Color", "#00EE17");
				}
				else {
					roiManager("Set Color", "red");
				}

				n++;
			}
			else if (z > currentSlice + sliceTolerance) {
				break;
			}
			
		}
		
		roiManager("show all");
		RoiManager.useNamesAsLabels(true);
		
	}
}