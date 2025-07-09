cfosImage = getTitle();
setSlice(1);

run("Put Behind [tab]");
overlayImage = getTitle();
setSlice(1);

selectImage(cfosImage);

prevSlice = -1;
while (true){
	wait(250);
	currentSlice = getSliceNumber();
	if(currentSlice != prevSlice){
		run("Remove Overlay");
		prevSlice = currentSlice;
		selectImage(overlayImage);
		setSlice(currentSlice);
		selectImage(cfosImage);
		wait(50);
		run("Add Image...", "image=" + overlayImage + " x=0 y=0 opacity=50 zero");
	}
}