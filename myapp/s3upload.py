'''
MIT License

Copyright (c) 2019 Arshdeep Bahga and Vijay Madisetti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import boto3

from myapp.settings import BUCKET_NAME

s3 = boto3.resource('s3') 
s3_client = boto3.client('s3')

bucket = s3.Bucket(BUCKET_NAME)

def upload_to_s3_bucket_root(source_file_folder, source_file_file_name, s3_folder, cleanup_local_copy=1):
	
	# Setup/Combine variables
	local_location = source_file_folder + source_file_file_name
	s3_location = s3_folder + source_file_file_name

	# Create the object
	obj = s3.Object(BUCKET_NAME, s3_location)
	obj.put(Body=open(local_location, 'rb'))
	
	# Delete the copy
	if cleanup_local_copy:
		os.remove(local_location)

	# Get a short-term access link
	url = get_presigned_url(s3_location, duration=3600)

	return url

def get_presigned_url(key, duration=3600):
	return s3_client.generate_presigned_url('get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key,
        },                                  
        ExpiresIn=duration
	)
