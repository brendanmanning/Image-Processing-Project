from django.shortcuts import render
from django.template import RequestContext
from myapp.forms import UploadFileForm
from PIL import Image, ImageOps,ImageFilter

from myapp.s3upload import upload_to_s3_bucket_root
from myapp.settings import PROCESSED_IMAGES_FOLDER, UNPROCESSED_IMAGES_FOLDER, S3_UNPROCESSED_FOLDER, S3_PROCESSED_FOLDER


def applyfilter(filename, preset):
	
	inputfile = UNPROCESSED_IMAGES_FOLDER + filename
	outputfile = PROCESSED_IMAGES_FOLDER + filename

	im = Image.open(inputfile)
	if preset=='gray':
		im = ImageOps.grayscale(im)

	if preset=='edge':
		im = ImageOps.grayscale(im)
		im = im.filter(ImageFilter.FIND_EDGES)

	if preset=='poster':
		im = ImageOps.posterize(im,3)

	if preset=='solar':
		im = ImageOps.solarize(im, threshold=80) 

	if preset=='blur':
		im = im.filter(ImageFilter.BLUR)
	
	if preset=='sepia':
		sepia = []
		r, g, b = (239, 224, 185)
		for i in range(255):
			sepia.extend((r*i/255, g*i/255, b*i/255))
		im = im.convert("L")
		im.putpalette(sepia)
		im = im.convert("RGB")

	im.save(outputfile)
	return outputfile

def handle_uploaded_file(f,preset):
	
	unprocessed_file = UNPROCESSED_IMAGES_FOLDER + f.name
	print("Trying to upload unprocessed file to: " + unprocessed_file)
	with open(unprocessed_file, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

	print("Applying filter to file")
	processed_file = applyfilter(f.name, preset)

	print("Trying to upload original and filtered images to S3...")
	original_file_location = upload_to_s3_bucket_root(UNPROCESSED_IMAGES_FOLDER, f.name, S3_UNPROCESSED_FOLDER, cleanup_local_copy=1)
	filtered_file_location = upload_to_s3_bucket_root(PROCESSED_IMAGES_FOLDER, f.name, S3_PROCESSED_FOLDER, cleanup_local_copy=1)

	print("Cleanup local copies")

	return filtered_file_location

def home(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			print(request.POST['preset'])
			print(request.FILES)
			preset=request.POST['preset']
			output_file_link = handle_uploaded_file(request.FILES['myfilefield'],preset)
			print(output_file_link)
			return render(request, 'process.html',{'output_file_link': output_file_link}) #, context_instance=RequestContext(request))
		else:
			print("form was invalid")
	else:
		form = UploadFileForm() 
	return render(request, 'index.html', {'form': form}) #, context_instance=RequestContext(request))

def process(request):
	return render(request, 'process.html', {})


