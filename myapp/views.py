from django.shortcuts import render
from django.template import RequestContext
from myapp.forms import UploadFileForm
from PIL import Image, ImageOps,ImageFilter

from myapp.s3upload import upload_to_s3_bucket_root
from myapp.settings import PROCESSED_IMAGES_FOLDER, UNPROCESSED_IMAGES_FOLDER, S3_UNPROCESSED_FOLDER, S3_PROCESSED_FOLDER


def applyfilter(filename, presets):
	
	inputfile = UNPROCESSED_IMAGES_FOLDER + filename
	outputfile = PROCESSED_IMAGES_FOLDER + filename

	im = Image.open(inputfile).convert('RGB')

	if presets['gray']:
		print("Applying gray filter...")
		im = ImageOps.grayscale(im)

	if presets['poster']:
		print("Applying poster filter...")
		im = ImageOps.posterize(im,3)

	if presets['solar']:
		print("Applying solar filter...")
		im = ImageOps.solarize(im, threshold=80) 

	if presets['blur']:
		print("Applying blur filter...")
		im = im.filter(ImageFilter.GaussianBlur(radius = 20)) 

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

	return original_file_location, filtered_file_location

def home(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			presets = {
				'gray': 'gray' in request.POST,
				'poster': 'poster' in request.POST,
				'blur': 'blur' in request.POST,
				'solar': 'solar' in request.POST
			}
			original_file_link, filtered_file_link = handle_uploaded_file(request.FILES['myfilefield'],presets)
			return render(request, 'process.html',{'original_file_link': original_file_link, 'filtered_file_link': filtered_file_link}) #, context_instance=RequestContext(request))
		else:
			print("form was invalid")
	else:
		form = UploadFileForm() 
	return render(request, 'index.html', {'form': form}) #, context_instance=RequestContext(request))

def process(request):
	return render(request, 'process.html', {})


